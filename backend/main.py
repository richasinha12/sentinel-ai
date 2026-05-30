"""
Sentinel AI — Unified Multi-Agent Intelligence Platform
Self-contained backend. Runs with only: fastapi uvicorn
Demo mode built-in — no external API keys required for the demo.
"""
from __future__ import annotations
import asyncio, json, uuid, os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── In-memory store (no DB needed for demo) ───────────────────────────────────
_signals: list[dict] = []
_insights: list[dict] = []

def _id(): return str(uuid.uuid4())
def _ts(offset_min=0): return (datetime.utcnow() - timedelta(minutes=offset_min)).isoformat() + "Z"

# ── Realistic demo data ───────────────────────────────────────────────────────
DEMO_SIGNALS = [
    # GTM Agent signals
    {"id": _id(), "agent": "gtm", "title": "HubSpot raised pricing 18% across all tiers",
     "summary": "HubSpot announced a pricing increase effective next quarter. Professional tier up from $800 to $944/mo. Sales teams should update competitive battlecards immediately.",
     "severity": "high", "source_url": "https://hubspot.com/pricing",
     "metadata": {"target": "hubspot.com", "type": "pricing"}, "timestamp": _ts(2)},
    {"id": _id(), "agent": "gtm", "title": "Salesforce posting 47 new AI engineer roles",
     "summary": "Salesforce is aggressively hiring AI/ML engineers — 47 open roles in SF and NYC. Signals a major Einstein AI v3 push. Prepare competitive response.",
     "severity": "medium", "source_url": "https://salesforce.com/careers",
     "metadata": {"target": "salesforce.com", "type": "hiring"}, "timestamp": _ts(5)},
    {"id": _id(), "agent": "gtm", "title": "Competitor G2 rating dropped 0.4 stars this month",
     "summary": "HubSpot's G2 rating fell from 4.4 → 4.0 in 30 days. Top complaints: price increase, slow support, missing AI features. High opportunity to capture dissatisfied customers.",
     "severity": "high", "source_url": "https://g2.com/products/hubspot",
     "metadata": {"target": "hubspot.com", "type": "review"}, "timestamp": _ts(10)},
    # Finance Agent signals
    {"id": _id(), "agent": "finance", "title": "Acme Corp announced 12% workforce reduction",
     "summary": "Acme Corp laid off 340 employees including their entire data team. CFO cited 'market headwinds'. Churn risk score: 78/100. CS team should reach out within 24 hours.",
     "severity": "critical", "source_url": "https://techcrunch.com",
     "metadata": {"company": "Acme Corp", "churn_score": 78, "risk_type": "layoff"}, "timestamp": _ts(1)},
    {"id": _id(), "agent": "finance", "title": "Globex CEO resigned, interim CFO appointed",
     "summary": "Globex's CEO resigned effective immediately. Board appointed CFO as interim. Leadership transitions correlate with 60% churn rate in first 90 days.",
     "severity": "high", "source_url": "https://bloomberg.com",
     "metadata": {"company": "Globex", "churn_score": 62, "risk_type": "leadership"}, "timestamp": _ts(8)},
    {"id": _id(), "agent": "finance", "title": "Macro: SaaS budget freezes up 34% YoY",
     "summary": "Gartner reports 34% more enterprises implementing SaaS budget freezes vs last year. Renewal conversations should emphasize ROI and consolidation value.",
     "severity": "medium", "source_url": "https://gartner.com",
     "metadata": {"type": "macro"}, "timestamp": _ts(20)},
    # Security Agent signals
    {"id": _id(), "agent": "security", "title": "Okta breach: 3rd-party vendor compromised",
     "summary": "Okta confirmed a breach via a third-party support vendor. Customer session tokens potentially exposed. CVE-2025-4821 published. Immediate action required for all Okta-dependent workflows.",
     "severity": "critical", "source_url": "https://sec.okta.com",
     "metadata": {"vendor": "Okta", "type": "breach", "cve": "CVE-2025-4821"}, "timestamp": _ts(0)},
    {"id": _id(), "agent": "security", "title": "CISA advisory: critical Stripe API vulnerability",
     "summary": "CISA issued advisory AA25-142A for a Stripe API authentication bypass. Affects all accounts using legacy API keys. Rotate keys immediately and audit transaction logs.",
     "severity": "high", "source_url": "https://cisa.gov",
     "metadata": {"vendor": "Stripe", "type": "regulatory", "cve": "CVE-2025-3301"}, "timestamp": _ts(15)},
    {"id": _id(), "agent": "security", "title": "AWS S3 misconfiguration pattern detected in wild",
     "summary": "Security researchers report a new S3 bucket misconfiguration pattern affecting 1,200+ companies. Check your bucket policies against the published checklist.",
     "severity": "medium", "source_url": "https://cisa.gov",
     "metadata": {"vendor": "AWS", "type": "cve"}, "timestamp": _ts(30)},
]

DEMO_INSIGHTS = [
    {"id": _id(), "title": "🎯 Competitor Distress = Your 30-Day Attack Window",
     "narrative": "HubSpot raised prices 18% while G2 ratings dropped 0.4 stars and they missed Q1 revenue targets. This trifecta signals internal pressure — their customers are actively evaluating alternatives RIGHT NOW. Historical data shows 23% of customers switch within 60 days of a price increase paired with satisfaction decline.",
     "severity": "critical",
     "recommended_actions": [
         "Launch targeted campaign to HubSpot customers: 'Switch and save 40%' — start this week",
         "Brief entire sales team with updated battlecard highlighting HubSpot price increase",
         "Set G2 alert to respond to every 1-3 star HubSpot review within 2 hours",
     ],
     "affected_domains": ["gtm", "finance"],
     "timestamp": _ts(0)},
    {"id": _id(), "title": "🔴 Acme Corp: Churn Risk Amplified by Okta Breach",
     "narrative": "Acme Corp is already at 78/100 churn risk due to layoffs. They also use Okta (confirmed via their tech stack). The Okta breach means their security team is now overwhelmed — making them even less likely to renew a non-critical SaaS tool. The combination of financial stress + security crisis creates a 48-hour intervention window.",
     "severity": "critical",
     "recommended_actions": [
         "CS to call Acme Corp within 2 hours — offer 3-month extension at current price",
         "Send Acme Corp our Okta breach mitigation guide to add value during their crisis",
         "Flag Acme Corp as 'at risk' in CRM — escalate to VP Customer Success immediately",
     ],
     "affected_domains": ["finance", "security"],
     "timestamp": _ts(1)},
    {"id": _id(), "title": "📊 Budget Freeze + Competitor Weakness = Consolidation Play",
     "narrative": "Macro SaaS budget freezes are up 34% while HubSpot's product satisfaction is declining. Enterprises under budget pressure actively consolidate tools. Sentinel's $500/month vs $13,500/month narrative is uniquely powerful right now — this is the moment to push the consolidation pitch.",
     "severity": "high",
     "recommended_actions": [
         "Update all outbound messaging to lead with consolidation ROI ($13,000/month savings)",
         "Create a 'SaaS consolidation calculator' landing page for inbound leads",
         "Target HubSpot + Salesforce joint customers — they're paying double and getting half",
     ],
     "affected_domains": ["gtm", "finance"],
     "timestamp": _ts(5)},
]

# ── WebSocket manager ─────────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self): self.active: list[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept(); self.active.append(ws)
    def disconnect(self, ws: WebSocket):
        if ws in self.active: self.active.remove(ws)
    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try: await ws.send_json(data)
            except: dead.append(ws)
        for ws in dead: self.active.remove(ws)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load demo data
    _signals.extend(DEMO_SIGNALS)
    _insights.extend(DEMO_INSIGHTS)
    yield

app = FastAPI(title="Sentinel AI", version="1.0.0", lifespan=lifespan)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ── Run agents (simulated with streaming) ────────────────────────────────────
class RunRequest(BaseModel):
    competitors: list[str] = []
    customers: list[str] = []
    vendors: list[str] = []

@app.post("/api/run")
async def run_agents(req: RunRequest):
    """Simulate agent runs with realistic streaming delays."""
    async def _stream():
        agents = [
            ("gtm",      [s for s in DEMO_SIGNALS if s["agent"] == "gtm"],      "mistralai/Mistral-7B-Instruct-v0.3", 1240),
            ("finance",  [s for s in DEMO_SIGNALS if s["agent"] == "finance"],  "microsoft/Phi-3-mini-4k-instruct",   980),
            ("security", [s for s in DEMO_SIGNALS if s["agent"] == "security"], "meta-llama/Meta-Llama-3-8B-Instruct", 1100),
        ]
        for agent, signals, model, ms in agents:
            await asyncio.sleep(1.2)  # realistic delay
            await manager.broadcast({
                "type": "agent_done", "agent": agent,
                "signal_count": len(signals), "model": model,
                "duration_ms": ms, "signals": signals,
            })
        await asyncio.sleep(1.5)  # synthesis delay
        await manager.broadcast({"type": "synthesis_done", "insights": DEMO_INSIGHTS})

    asyncio.create_task(_stream())
    return {"status": "running", "message": "Agents started — watch the dashboard for live updates"}

# ── REST endpoints ────────────────────────────────────────────────────────────
@app.get("/api/signals")
async def get_signals(agent: Optional[str] = None, severity: Optional[str] = None, limit: int = 50):
    data = _signals
    if agent: data = [s for s in data if s["agent"] == agent]
    if severity: data = [s for s in data if s["severity"] == severity]
    return data[:limit]

@app.get("/api/insights")
async def get_insights(limit: int = 20):
    return _insights[:limit]

@app.get("/api/stats")
async def get_stats():
    return {
        "total_signals": len(_signals),
        "total_insights": len(_insights),
        "agents": {
            "gtm":      len([s for s in _signals if s["agent"] == "gtm"]),
            "finance":  len([s for s in _signals if s["agent"] == "finance"]),
            "security": len([s for s in _signals if s["agent"] == "security"]),
        },
        "critical": len([s for s in _signals if s["severity"] == "critical"]),
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel-ai", "version": "1.0.0"}
