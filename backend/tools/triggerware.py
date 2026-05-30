"""TriggerWare.ai — automated workflow triggers: CRM updates, Slack alerts, tickets."""
from __future__ import annotations
import httpx
import hmac, hashlib
from typing import Any
from backend.config import settings
from backend.agents.types import SynthesisInsight, Signal, SignalSeverity

BASE = settings.TRIGGERWARE_BASE_URL
HEADERS = {"Authorization": f"Bearer {settings.TRIGGERWARE_API_KEY}", "Content-Type": "application/json"}


async def _trigger(workflow_id: str, payload: dict) -> dict:
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as c:
        r = await c.post(f"{BASE}/workflows/{workflow_id}/trigger", json=payload)
        r.raise_for_status()
        return r.json()


async def trigger_crm_update(signal: Signal) -> dict:
    """GTM: push competitor intel to CRM as a deal note."""
    return await _trigger("crm_update", {
        "signal_id": signal.id,
        "title": signal.title,
        "summary": signal.summary,
        "severity": signal.severity,
        "source_url": signal.source_url,
    })


async def trigger_cs_alert(signal: Signal) -> dict:
    """Finance: alert Customer Success team about churn risk."""
    return await _trigger("cs_churn_alert", {
        "signal_id": signal.id,
        "churn_score": signal.metadata.get("churn_score", 0),
        "company": signal.metadata.get("company", "Unknown"),
        "summary": signal.summary,
    })


async def trigger_security_incident(signal: Signal) -> dict:
    """Security: create incident ticket + draft customer notification."""
    return await _trigger("security_incident", {
        "signal_id": signal.id,
        "severity": signal.severity,
        "vendor": signal.metadata.get("vendor", "Unknown"),
        "summary": signal.summary,
        "cve": signal.metadata.get("cve"),
    })


async def trigger_synthesis_broadcast(insight: SynthesisInsight) -> dict:
    """Cross-agent: broadcast synthesis insight to all relevant teams."""
    workflow = "critical_synthesis" if insight.severity == SignalSeverity.CRITICAL else "synthesis_broadcast"
    return await _trigger(workflow, {
        "insight_id": insight.id,
        "title": insight.title,
        "narrative": insight.narrative,
        "actions": insight.recommended_actions,
        "domains": insight.affected_domains,
        "severity": insight.severity,
    })


def verify_webhook(body: bytes, signature: str) -> bool:
    """Verify incoming TriggerWare webhook signature."""
    expected = hmac.new(settings.TRIGGERWARE_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
