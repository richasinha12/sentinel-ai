"""Sentinel orchestrator — runs all agents in parallel, feeds results to synthesis engine."""
from __future__ import annotations
import asyncio
from typing import Callable, Awaitable, Any
from backend.agents import gtm_agent, finance_agent, security_agent
from backend.agents.synthesis_engine import synthesize
from backend.agents.types import AgentRunResult, SynthesisInsight


async def run_all(
    gtm_targets: list[str] = None,
    finance_companies: list[str] = None,
    security_vendors: list[str] = None,
    on_agent_done: Callable[[AgentRunResult], Awaitable[None]] = None,
) -> tuple[list[AgentRunResult], list[SynthesisInsight]]:
    """Run all 3 agents in parallel, then synthesize. Calls on_agent_done for real-time streaming."""

    async def _run_and_notify(coro, *args, **kwargs):
        result = await coro(*args, **kwargs)
        if on_agent_done:
            await on_agent_done(result)
        return result

    results = await asyncio.gather(
        _run_and_notify(gtm_agent.run, gtm_targets or []),
        _run_and_notify(finance_agent.run, finance_companies or []),
        _run_and_notify(security_agent.run, security_vendors or []),
        return_exceptions=True,
    )

    # Filter out exceptions, keep successful results
    valid = [r for r in results if isinstance(r, AgentRunResult)]
    insights = await synthesize(valid)
    return valid, insights
