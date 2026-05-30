"""Demo mode — returns realistic mock data when API keys are not configured.
Set DEMO_MODE=true in .env to use this instead of live APIs.
"""
from backend.agents.types import (
    AgentType, Signal, SignalSeverity, SynthesisInsight, AgentRunResult
)
from datetime import datetime, timedelta
import uuid

def _id(): return str(uuid.uuid4())
_now = datetime.utcnow

GTM_SIGNALS = [
    Signal(id=_id(), agent=AgentType.GTM, title="HubSpot raised pricing 18% across all tiers",
           summary="HubSpot announced a pricing increase effective next quarter. Professional tier up from $800 to $944/mo. Sales teams should update competitive battlecards immediately.",
           severity=SignalSeverity.HIGH, source_url="https://hubspot.com/pricing",
           metadata={"target": "hubspot.com", "type": "pricing"}, timestamp=_now()),
    Signal(id=_id(), agent=AgentType.GTM, title="Salesforce posting 47 new AI engineer roles",
           summary="Salesforce is aggressively hiring AI/ML engineers, suggesting a major product push. 47 open roles in SF and NYC. Likely building Einstein AI v3.",
           severity=SignalSeverity.MEDIUM, source_url="https://salesforce.com/careers",
           metadata={"target": "salesforce.com", "type": "hiring"}, timestamp=_now() - timedelta(minutes=5)),
    Signal(id=_id(), agent=AgentType.GTM, title="Competitor G2 reviews drop 0.4 stars this month",
           summary="HubSpot's G2 rating dropped from 4.4 to 4.0 in 30 days. Top complaints: price increase, slow support, missing AI features. Opportunity to capture dissatisfied customers.",
           severity=SignalSeverity.HIGH, source_url="https://g2.com/products/hubspot",
           metadata={"target": "hubspot.com", "type": "review"}, timestamp=_now() - timedelta(minutes=10)),
]

FINANCE_SIGNALS = [
    Signal(id=_id(), agent=AgentType.FINANCE, title="Acme Corp announced 12% workforce reduction",
           summary="Acme Corp laid off 340 employees including their entire data team. CFO cited 'market headwinds'. Churn risk score: 78/100. CS team should reach out within 24 hours.",
           severity=SignalSeverity.CRITICAL, source_url="https://techcrunch.com",
           metadata={"company": "acme-corp", "churn_score": 78, "risk_type": "layoff"}, timestamp=_now() - timedelta(minutes=2)),
    Signal(id=_id(), agent=AgentType.FINANCE, title="Globex CEO resigned, interim appointed",
           summary="Globex's CEO John Smith resigned effective immediately. Board appointed CFO as interim. Leadership transitions historically correlate with 60% churn rate in first 90 days.",
           severity=SignalSeverity.HIGH, source_url="https://bloomberg.com",
           metadata={"company": "globex", "churn_score": 62, "risk_type": "leadership"}, timestamp=_now() - timedelta(minutes=8)),
]

SECURITY_SIGNALS = [
    Signal(id=_id(), agent=AgentType.SECURITY, title="Okta breach: 3rd party vendor compromised",
           summary="Okta confirmed a breach via a third-party support vendor. Customer session tokens potentially exposed. CVE-2025-4821 published. Immediate action required for all Okta-dependent workflows.",
           severity=SignalSeverity.CRITICAL, source_url="https://sec.okta.com/articles/2025",
           metadata={"vendor": "okta", "type": "breach", "cve": "CVE-2025-4821"}, timestamp=_now() - timedelta(minutes=1)),
    Signal(id=_id(), agent=AgentType.SECURITY, title="CISA advisory: critical Stripe API vulnerability",
           summary="CISA issued advisory AA25-142A for a Stripe API authentication bypass. Affects all accounts using legacy API keys. Rotate keys immediately and audit transaction logs.",
           severity=SignalSeverity.HIGH, source_url="https://cisa.gov/advisories",
           metadata={"vendor": "stripe", "type": "regulatory", "cve": "CVE-2025-3301"}, timestamp=_now() - timedelta(minutes=15)),
]

SYNTHESIS_INSIGHTS = [
    SynthesisInsight(
        id=_id(),
        title="Competitor Distress = Your Attack Window",
        narrative="HubSpot raised prices 18% while simultaneously seeing G2 ratings drop and missing Q1 revenue targets. This trifecta signals internal pressure — their customers are actively evaluating alternatives RIGHT NOW. This is a 30-day window to capture churning HubSpot accounts.",
        severity=SignalSeverity.CRITICAL,
        signals=GTM_SIGNALS[:2],
        recommended_actions=[
            "Launch targeted campaign to HubSpot customers with 'switch and save 40%' messaging",
            "Brief sales team with updated battlecard highlighting HubSpot price increase",
            "Set up G2 review monitoring alert — respond to every 1-3 star HubSpot review",
        ],
        affected_domains=[AgentType.GTM, AgentType.FINANCE],
        timestamp=_now(),
    ),
    SynthesisInsight(
        id=_id(),
        title="Acme Corp: Churn Risk Amplified by Okta Breach",
        narrative="Acme Corp is already at 78/100 churn risk due to layoffs. They also use Okta (confirmed via their tech stack). The Okta breach means their security team is now overwhelmed — making them even less likely to renew a non-critical SaaS tool. Immediate CS intervention needed.",
        severity=SignalSeverity.CRITICAL,
        signals=[FINANCE_SIGNALS[0], SECURITY_SIGNALS[0]],
        recommended_actions=[
            "CS to call Acme Corp within 2 hours — offer 3-month extension at current price",
            "Send Acme Corp our Okta breach mitigation guide to add value during their crisis",
            "Flag Acme Corp deal as 'at risk' in CRM — escalate to VP Customer Success",
        ],
        affected_domains=[AgentType.FINANCE, AgentType.SECURITY],
        timestamp=_now() - timedelta(minutes=1),
    ),
]


async def demo_run_all():
    """Return mock agent results and synthesis insights for demo."""
    import asyncio
    await asyncio.sleep(0.5)  # simulate processing time

    results = [
        AgentRunResult(agent=AgentType.GTM, signals=GTM_SIGNALS,
                       model_used="mistralai/Mistral-7B-Instruct-v0.3", duration_ms=1240),
        AgentRunResult(agent=AgentType.FINANCE, signals=FINANCE_SIGNALS,
                       model_used="microsoft/Phi-3-mini-4k-instruct", duration_ms=980),
        AgentRunResult(agent=AgentType.SECURITY, signals=SECURITY_SIGNALS,
                       model_used="meta-llama/Meta-Llama-3-8B-Instruct", duration_ms=1100),
    ]
    return results, SYNTHESIS_INSIGHTS
