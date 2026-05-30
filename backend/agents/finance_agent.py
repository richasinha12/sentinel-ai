"""Finance & Market Intelligence Agent — layoffs, leadership changes, hiring trends, churn risk."""
from __future__ import annotations
import time, json
from backend.agents.types import AgentType, Signal, SignalSeverity, AgentRunResult
from backend.tools.bright_data import serp_search, mcp_query
from backend.tools.featherless import featherless_infer
from backend.tools.cognee import remember
from backend.tools.triggerware import trigger_cs_alert


WATCH_COMPANIES: list[str] = []  # populated from DB/config at runtime

RISK_SYSTEM = """You are a financial risk analyst. Given news about a company, output JSON:
{"churn_score": 0-100, "signals": [{"title": str, "summary": str, "severity": "low|medium|high|critical", "risk_type": "layoff|leadership|revenue|hiring"}]}
churn_score: 0=healthy, 100=imminent churn."""


async def _score_company(company: str) -> tuple[list[Signal], str]:
    signals = []

    # SERP: layoffs, leadership changes, earnings
    results = await serp_search(
        f'"{company}" layoffs OR "CEO resigned" OR "missed revenue" OR "hiring freeze" OR "funding"', num=8
    )
    snippets = "\n".join(r.get("snippet", "") + " " + r.get("title", "") for r in results[:8])

    # Featherless: risk scoring (phi-3 mini — fast)
    raw, model = await featherless_infer(
        "risk_scoring",
        f"Company: {company}\nNews:\n{snippets}",
        system=RISK_SYSTEM,
    )

    try:
        data = json.loads(raw)
        churn_score = data.get("churn_score", 0)
        for s in data.get("signals", []):
            severity = SignalSeverity(s.get("severity", "medium"))
            sig = Signal(
                agent=AgentType.FINANCE,
                title=s["title"],
                summary=s["summary"],
                severity=severity,
                metadata={"company": company, "churn_score": churn_score, "risk_type": s.get("risk_type")},
            )
            signals.append(sig)
            await remember(sig)
            if churn_score >= 60 or severity in (SignalSeverity.HIGH, SignalSeverity.CRITICAL):
                await trigger_cs_alert(sig)
    except (json.JSONDecodeError, KeyError):
        model = "none"

    return signals, model


async def run(companies: list[str] = None) -> AgentRunResult:
    t0 = time.time()
    targets = companies or WATCH_COMPANIES
    all_signals: list[Signal] = []
    last_model = "none"

    # Also watch macro signals via MCP
    try:
        macro = await mcp_query("search_engine", {
            "query": "tech layoffs OR SaaS churn OR enterprise budget cuts 2025", "count": 5
        })
        if macro:
            sig = Signal(
                agent=AgentType.FINANCE,
                title="Macro Market Signal",
                summary=str(macro)[:500],
                severity=SignalSeverity.LOW,
                metadata={"type": "macro"},
            )
            all_signals.append(sig)
            await remember(sig)
    except Exception:
        pass

    for company in targets:
        sigs, model = await _score_company(company)
        all_signals.extend(sigs)
        last_model = model

    return AgentRunResult(
        agent=AgentType.FINANCE,
        signals=all_signals,
        model_used=last_model,
        duration_ms=int((time.time() - t0) * 1000),
    )
