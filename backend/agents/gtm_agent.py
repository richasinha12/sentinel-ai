"""GTM Intelligence Agent — monitors competitor pricing, job postings, G2 reviews, product updates."""
from __future__ import annotations
import time, json
from backend.agents.types import AgentType, Signal, SignalSeverity, AgentRunResult
from backend.tools.bright_data import serp_search, scrape_url, mcp_query
from backend.tools.featherless import featherless_infer
from backend.tools.cognee import remember
from backend.tools.triggerware import trigger_crm_update


COMPETITOR_DOMAINS = ["competitor1.com", "competitor2.com"]  # configured per deployment

EXTRACTION_SYSTEM = """You are a GTM intelligence analyst. Extract structured competitor signals from web content.
Return JSON: {"signals": [{"title": str, "summary": str, "severity": "low|medium|high|critical", "type": str}]}"""


async def run(targets: list[str] = COMPETITOR_DOMAINS) -> AgentRunResult:
    t0 = time.time()
    signals: list[Signal] = []

    for target in targets:
        # 1. SERP: find recent news about competitor
        results = await serp_search(f'site:{target} OR "{target}" pricing OR "product update" OR "job posting"', num=5)

        # 2. MCP: scrape competitor pricing page as markdown
        try:
            pricing_md = await mcp_query("scrape_as_markdown", {"url": f"https://{target}/pricing"})
        except Exception:
            pricing_md = {}

        # 3. Featherless: extract signals from SERP snippets (fast, cheap open-source model)
        serp_text = "\n".join(r.get("snippet", "") for r in results[:5])
        raw_extraction, model = await featherless_infer(
            "extraction",
            f"Extract GTM signals from:\n{serp_text}\n\nPricing page:\n{json.dumps(pricing_md)[:1000]}",
            system=EXTRACTION_SYSTEM,
        )

        try:
            extracted = json.loads(raw_extraction)
            for s in extracted.get("signals", []):
                sig = Signal(
                    agent=AgentType.GTM,
                    title=s["title"],
                    summary=s["summary"],
                    severity=SignalSeverity(s.get("severity", "medium")),
                    source_url=f"https://{target}",
                    metadata={"target": target, "type": s.get("type", "general")},
                )
                signals.append(sig)
                await remember(sig)
                if sig.severity in (SignalSeverity.HIGH, SignalSeverity.CRITICAL):
                    await trigger_crm_update(sig)
        except (json.JSONDecodeError, KeyError):
            pass

        # 4. G2 reviews via Bright Data scraper dataset
        try:
            reviews = await mcp_query("search_engine", {"query": f"{target} reviews site:g2.com", "count": 3})
            if reviews:
                sig = Signal(
                    agent=AgentType.GTM,
                    title=f"G2 Review Activity: {target}",
                    summary=str(reviews)[:400],
                    severity=SignalSeverity.LOW,
                    source_url="https://g2.com",
                    metadata={"target": target, "type": "review"},
                )
                signals.append(sig)
                await remember(sig)
        except Exception:
            pass

    return AgentRunResult(
        agent=AgentType.GTM,
        signals=signals,
        model_used=model if signals else "none",
        duration_ms=int((time.time() - t0) * 1000),
    )
