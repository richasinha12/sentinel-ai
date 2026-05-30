# Sentinel AI — Kiro Project Steering

## Project
Unified multi-agent intelligence platform: GTM + Finance + Security agents with Cross-Agent Synthesis.

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy async, WebSockets
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, Zustand
- AI: Anthropic Claude (synthesis), Featherless AI (per-agent inference)
- Data: Bright Data (SERP, Unlocker, Scraper API, Browser, MCP)
- Memory: Cognee
- Workflows: TriggerWare.ai

## Code conventions
- All backend modules use async/await
- Pydantic models for all data shapes
- Featherless handles extraction/classification/summarization/risk-scoring
- Claude only used in synthesis_engine.py — never in individual agents
- Frontend state lives in Zustand store only (no prop drilling)
- WebSocket broadcasts every agent result in real-time

## File structure
- backend/agents/ — one file per agent + orchestrator + synthesis
- backend/tools/ — one file per external integration
- frontend/src/components/ — pure UI components, no fetch calls
- frontend/src/pages/ — pages own data fetching

## Do not
- Add REST polling — use WebSocket for live updates
- Use synchronous httpx calls — always async
- Import agents directly in main.py — use orchestrator only
