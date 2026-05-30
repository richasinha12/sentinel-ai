"""Sentinel AI — FastAPI backend with REST API + WebSocket real-time updates."""
from __future__ import annotations
import asyncio, json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional

from backend.config import settings
from backend.database import init_db, SessionLocal, SignalModel, InsightModel, WatchlistModel
from backend.agents.orchestrator import run_all
from backend.agents.types import AgentRunResult, SynthesisInsight, Signal
from backend.tools.triggerware import verify_webhook


# ── WebSocket connection manager ──────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Sentinel AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS.split(","),
                   allow_methods=["*"], allow_headers=["*"])


async def get_db():
    async with SessionLocal() as session:
        yield session


# ── WebSocket endpoint ────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ── Run agents ────────────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    competitors: list[str] = []
    customers: list[str] = []
    vendors: list[str] = []


@app.post("/api/run")
async def run_agents(req: RunRequest, db: AsyncSession = Depends(get_db)):
    """Trigger a full agent run. Streams progress via WebSocket."""

    async def on_agent_done(result: AgentRunResult):
        # Persist signals
        for sig in result.signals:
            db.add(SignalModel(
                id=sig.id, agent=sig.agent, title=sig.title, summary=sig.summary,
                severity=sig.severity, source_url=sig.source_url,
                metadata_=sig.metadata, timestamp=sig.timestamp,
            ))
        await db.commit()
        # Broadcast to dashboard
        await manager.broadcast({
            "type": "agent_done",
            "agent": result.agent,
            "signal_count": len(result.signals),
            "model": result.model_used,
            "duration_ms": result.duration_ms,
            "signals": [s.model_dump(mode="json") for s in result.signals],
        })

    if settings.DEMO_MODE:
        from backend.demo_mode import demo_run_all
        results, insights = await demo_run_all()
        for r in results:
            await on_agent_done(r)
    else:
        results, insights = await run_all(
            gtm_targets=req.competitors,
            finance_companies=req.customers,
            security_vendors=req.vendors,
            on_agent_done=on_agent_done,
        )

    # Persist insights
    for ins in insights:
        db.add(InsightModel(
            id=ins.id, title=ins.title, narrative=ins.narrative,
            severity=ins.severity, recommended_actions=ins.recommended_actions,
            affected_domains=ins.affected_domains,
            signal_ids=[s.id for s in ins.signals],
            timestamp=ins.timestamp,
        ))
    await db.commit()

    # Broadcast synthesis
    await manager.broadcast({
        "type": "synthesis_done",
        "insights": [i.model_dump(mode="json") for i in insights],
    })

    return {
        "agents_run": len(results),
        "total_signals": sum(len(r.signals) for r in results),
        "insights": len(insights),
    }


# ── REST endpoints ────────────────────────────────────────────────────────────
@app.get("/api/signals")
async def get_signals(agent: Optional[str] = None, severity: Optional[str] = None,
                      limit: int = 50, db: AsyncSession = Depends(get_db)):
    q = select(SignalModel).order_by(desc(SignalModel.timestamp)).limit(limit)
    if agent:
        q = q.where(SignalModel.agent == agent)
    if severity:
        q = q.where(SignalModel.severity == severity)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "agent": r.agent, "title": r.title, "summary": r.summary,
             "severity": r.severity, "source_url": r.source_url,
             "metadata": r.metadata_, "timestamp": r.timestamp} for r in rows]


@app.get("/api/insights")
async def get_insights(limit: int = 20, db: AsyncSession = Depends(get_db)):
    q = select(InsightModel).order_by(desc(InsightModel.timestamp)).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "title": r.title, "narrative": r.narrative,
             "severity": r.severity, "recommended_actions": r.recommended_actions,
             "affected_domains": r.affected_domains, "timestamp": r.timestamp} for r in rows]


@app.get("/api/watchlist")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WatchlistModel))
    rows = result.scalars().all()
    return [{"id": r.id, "name": r.name, "category": r.category, "domain": r.domain} for r in rows]


class WatchlistItem(BaseModel):
    name: str
    category: str  # competitor|customer|vendor
    domain: str    # gtm|finance|security|all


@app.post("/api/watchlist")
async def add_watchlist(item: WatchlistItem, db: AsyncSession = Depends(get_db)):
    row = WatchlistModel(name=item.name, category=item.category, domain=item.domain)
    db.add(row)
    await db.commit()
    return {"status": "added"}


@app.delete("/api/watchlist/{item_id}")
async def delete_watchlist(item_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(WatchlistModel, item_id)
    if not row:
        raise HTTPException(404, "Not found")
    await db.delete(row)
    await db.commit()
    return {"status": "deleted"}


# ── TriggerWare webhook receiver ──────────────────────────────────────────────
@app.post("/api/webhooks/triggerware")
async def triggerware_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-TriggerWare-Signature", "")
    if not verify_webhook(body, sig):
        raise HTTPException(401, "Invalid signature")
    payload = json.loads(body)
    await manager.broadcast({"type": "workflow_update", "payload": payload})
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel-ai"}
