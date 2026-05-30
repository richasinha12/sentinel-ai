"""Cognee — agent memory: store signals, retrieve relevant context for synthesis."""
from __future__ import annotations
import httpx
from typing import Any
from backend.config import settings
from backend.agents.types import Signal

BASE = settings.COGNEE_BASE_URL
HEADERS = {"Authorization": f"Bearer {settings.COGNEE_API_KEY}", "Content-Type": "application/json"}


async def remember(signal: Signal) -> None:
    """Store a signal in Cognee memory graph."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as c:
        await c.post(f"{BASE}/add", json={
            "text": f"{signal.title}\n{signal.summary}",
            "metadata": {"agent": signal.agent, "severity": signal.severity,
                         "id": signal.id, "timestamp": signal.timestamp.isoformat()},
        })


async def recall(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Retrieve relevant past signals from Cognee memory graph."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as c:
        r = await c.post(f"{BASE}/search", json={"query": query, "limit": limit})
        r.raise_for_status()
        return r.json().get("results", [])


async def cognee_context_for_synthesis(topic: str) -> str:
    """Get formatted memory context string for Claude synthesis prompt."""
    memories = await recall(topic, limit=15)
    if not memories:
        return "No prior memory context."
    lines = [f"- [{m.get('metadata', {}).get('agent', '?')}] {m.get('text', '')[:200]}" for m in memories]
    return "\n".join(lines)
