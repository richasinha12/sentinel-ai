"""Security & Compliance Agent — vendor breaches, CVEs, regulatory changes, credential leaks."""
from __future__ import annotations
import time, json
from backend.agents.types import AgentType, Signal, SignalSeverity, AgentRunResult
from backend.tools.bright_data import serp_search, scrape_url, mcp_query
from backend.tools.featherless import featherless_infer
from backend.tools.cognee import remember
from backend.tools.triggerware import trigger_security_incident


VENDOR_WATCH: list[str] = []  # e.g. ["aws", "okta", "salesforce"]
REGULATORY_FEEDS = [
    "https://www.cisa.gov/news-events/cybersecurity-advisories",
    "https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=critical",
]

SEC_SYSTEM = """You are a security analyst. Extract security signals from content. Return JSON:
{"signals": [{"title": str, "summary": str, "severity": "low|medium|high|critical",
"type": "breach|cve|regulatory|credential_leak|ciso_change", "vendor": str, "cve": str|null}]}"""


async def run(vendors: list[str] = None) -> AgentRunResult:
    t0 = time.time()
    targets = vendors or VENDOR_WATCH
    signals: list[Signal] = []
    last_model = "none"

    # 1. Vendor breach monitoring via SERP
    for vendor in targets:
        results = await serp_search(
            f'"{vendor}" breach OR "data leak" OR "CVE" OR "vulnerability" OR "CISO" 2025', num=6
        )
        snippets = "\n".join(r.get("title", "") + ": " + r.get("snippet", "") for r in results[:6])
        raw, model = await featherless_infer("classification", snippets, system=SEC_SYSTEM)
        last_model = model
        try:
            data = json.loads(raw)
            for s in data.get("signals", []):
                sig = Signal(
                    agent=AgentType.SECURITY,
                    title=s["title"],
                    summary=s["summary"],
                    severity=SignalSeverity(s.get("severity", "medium")),
                    metadata={"vendor": s.get("vendor", vendor), "type": s.get("type"),
                               "cve": s.get("cve")},
                )
                signals.append(sig)
                await remember(sig)
                if sig.severity in (SignalSeverity.HIGH, SignalSeverity.CRITICAL):
                    await trigger_security_incident(sig)
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Regulatory feed via Web Unlocker + MCP
    try:
        reg_content = await mcp_query("scrape_as_markdown", {"url": REGULATORY_FEEDS[0]})
        if reg_content:
            raw, model = await featherless_infer(
                "summarization",
                f"Summarize new regulatory advisories:\n{str(reg_content)[:2000]}",
                system="Return JSON: {\"signals\": [{\"title\": str, \"summary\": str, \"severity\": str, \"type\": \"regulatory\", \"vendor\": \"CISA\", \"cve\": null}]}"
            )
            last_model = model
            data = json.loads(raw)
            for s in data.get("signals", []):
                sig = Signal(
                    agent=AgentType.SECURITY,
                    title=s["title"],
                    summary=s["summary"],
                    severity=SignalSeverity(s.get("severity", "medium")),
                    source_url=REGULATORY_FEEDS[0],
                    metadata={"type": "regulatory", "vendor": "CISA"},
                )
                signals.append(sig)
                await remember(sig)
    except Exception:
        pass

    return AgentRunResult(
        agent=AgentType.SECURITY,
        signals=signals,
        model_used=last_model,
        duration_ms=int((time.time() - t0) * 1000),
    )
