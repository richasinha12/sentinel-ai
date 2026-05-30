"""Cross-Agent Synthesis Engine — Claude correlates signals from all 3 agents into unique insights."""
from __future__ import annotations
import json
import anthropic
from backend.agents.types import AgentType, Signal, SignalSeverity, SynthesisInsight, AgentRunResult
from backend.tools.cognee import cognee_context_for_synthesis
from backend.tools.triggerware import trigger_synthesis_broadcast

_claude = anthropic.AsyncAnthropic()

SYNTHESIS_SYSTEM = """You are Sentinel AI's synthesis engine. You receive signals from three agents:
- GTM Agent: competitor intelligence, market moves
- Finance Agent: customer financial health, churn risk
- Security Agent: vendor breaches, compliance changes

Your job: find NON-OBVIOUS correlations between signals that no single agent could see alone.
Example: GTM sees competitor raised prices + Finance sees competitor missed revenue + Security sees competitor's CISO resigned
→ Synthesis: "Competitor in distress — attack window open, but their customers may be looking for alternatives"

Return JSON:
{
  "insights": [
    {
      "title": str,
      "narrative": str (2-3 sentences explaining the cross-domain pattern),
      "severity": "low|medium|high|critical",
      "affected_domains": ["gtm"|"finance"|"security"],
      "recommended_actions": [str, str, str],
      "signal_ids": [str]
    }
  ]
}
Only return insights where signals from 2+ different agents are correlated. Skip single-agent findings."""


async def synthesize(results: list[AgentRunResult]) -> list[SynthesisInsight]:
    """Run Claude synthesis over all agent signals + Cognee memory context."""
    all_signals: list[Signal] = []
    for r in results:
        all_signals.extend(r.signals)

    if len(all_signals) < 2:
        return []

    # Build signal summary for Claude
    signal_lines = []
    for s in all_signals:
        signal_lines.append(
            f"[{s.agent.upper()}|{s.severity}|id:{s.id}] {s.title}: {s.summary[:200]}"
        )

    # Enrich with Cognee memory (historical patterns)
    memory_ctx = await cognee_context_for_synthesis("competitor distress churn security breach")

    prompt = f"""Current signals detected:
{chr(10).join(signal_lines)}

Historical memory context (past patterns):
{memory_ctx}

Find cross-agent correlations and generate synthesis insights."""

    resp = await _claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.content[0].text
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Claude sometimes wraps in markdown — strip it
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group()) if match else {"insights": []}

    insights: list[SynthesisInsight] = []
    signal_map = {s.id: s for s in all_signals}

    for item in data.get("insights", []):
        contributing = [signal_map[sid] for sid in item.get("signal_ids", []) if sid in signal_map]
        insight = SynthesisInsight(
            title=item["title"],
            narrative=item["narrative"],
            severity=SignalSeverity(item.get("severity", "medium")),
            signals=contributing,
            recommended_actions=item.get("recommended_actions", []),
            affected_domains=[AgentType(d) for d in item.get("affected_domains", [])],
        )
        insights.append(insight)
        # Trigger automated workflow for each insight
        await trigger_synthesis_broadcast(insight)

    return insights
