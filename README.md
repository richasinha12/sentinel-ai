# 🛡️ Sentinel AI — Unified Autonomous Multi-Agent Intelligence Platform for Enterprise Operations

> **Sentinel AI is a 24/7 autonomous multi-agent intelligence platform that unifies sales, finance, and security operations into a single system. It continuously monitors the web, detects critical events, and delivers real-time insights and alerts to relevant teams, helping organizations replace fragmented tool stacks costing $13.5K+/month with a unified $500/month solution.

The system uses specialized agents: GTM (Mistral-7B for entity extraction), Finance (Phi-3-mini for numerical reasoning), and Security (Llama-3-8B for threat classification), powered by Bright Data for web data acquisition and Featherless AI for scalable open-source inference.

A Cross-Agent Synthesis Engine (Claude Opus + Cognee) connects insights across domains using memory and knowledge graphs to uncover non-obvious business correlations.

Automated workflows via TriggerWare convert insights into action—pushing GTM signals to CRMs, triggering churn alerts (>60) with retention playbooks, and creating security incident tickets and customer notifications.

Impact: Reduces tool fragmentation, improves decision speed, and enables real-time, cross-functional intelligence for faster, data-driven business actions.**

Built entirely with **Kiro CLI** for the hackathon.

---

## The Problem

Companies pay **$13,500+/month** across 5+ siloed tools that never talk to each other.  
Sentinel replaces all of them for **$500/month** — and connects the dots between them.


What It Is
A 24/7 autonomous AI agent that monitors the web across sales, finance, and security — and automatically alerts the right team when something important happens.
Problem
Companies pay $13,500+/month across 5+ siloed tools that never talk to each other. Sentinel replaces all of them for $500/month and connects the dots between them.
3 Agents, Running Silently in Background
GTM Agent — Watches competitor pricing, product updates, job postings, G2 reviews → Auto-updates CRM, sends sales talking points, flags affected deals
Finance Agent — Watches customer layoffs, leadership changes, hiring trends → Calculates churn risk score, alerts Customer Success, generates retention playbook
Security Agent — Watches vendor breaches, regulatory changes, credential leaks → Generates incident report, creates compliance ticket, drafts customer notification

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Sentinel AI Platform                     │
├──────────────┬──────────────────┬───────────────────────────┤
│  GTM Agent   │  Finance Agent   │    Security Agent         │
│  🎯           │  📊               │    🛡️                      │
│  Bright Data │  Bright Data     │    Bright Data            │
│  SERP + MCP  │  SERP + MCP      │    Unlocker + MCP         │
│  Featherless │  Featherless     │    Featherless            │
│  (Mistral)   │  (Phi-3)         │    (Llama-3)              │
├──────────────┴──────────────────┴───────────────────────────┤
│              Cross-Agent Synthesis Engine                    │
│              🧠 Claude claude-opus-4-5 + Cognee Memory        │
├─────────────────────────────────────────────────────────────┤
│              TriggerWare.ai Automated Workflows              │
│   CRM Update │ CS Alert │ Security Ticket │ Team Broadcast  │
├─────────────────────────────────────────────────────────────┤
│         FastAPI Backend + WebSocket Real-time Updates        │
│              React Dashboard (Tailwind + Zustand)            │
└─────────────────────────────────────────────────────────────┘
```

---

## Partner Technology Integration

### 🌐 Bright Data (All 5 tools)
| Tool | Usage |
|------|-------|
| **SERP API** | Real-time Google search for competitor news, layoffs, CVEs |
| **Web Unlocker** | Bypass anti-bot to scrape competitor pricing pages |
| **Web Scraper API** | Trigger dataset collectors for G2 reviews, job postings |
| **Scraping Browser** | Playwright CDP sessions for JS-heavy pages |
| **MCP Server** | `scrape_as_markdown`, `search_engine` tool calls from agents |

### 🤖 Featherless AI (Open-source inference)
Each agent uses the best open-source model for its task:
- **Mistral-7B** → GTM extraction (fast, accurate entity extraction)
- **Phi-3-mini** → Finance risk scoring (efficient numerical reasoning)
- **Llama-3-8B** → Security classification (strong at threat categorization)
- **Qwen2-7B** → Summarization (multilingual, long-context)

### 🧠 Cognee (Agent Memory)
- Every signal is stored in Cognee's knowledge graph
- Synthesis engine retrieves historical patterns before Claude runs
- Enables "I've seen this pattern before" reasoning across runs

### ⚡ TriggerWare.ai (Automated Workflows)
| Trigger | Action |
|---------|--------|
| High-severity GTM signal | Push to CRM as deal note + sales talking points |
| Churn score ≥ 60 | Alert Customer Success + generate retention playbook |
| Critical security signal | Create incident ticket + draft customer notification |
| Synthesis insight | Broadcast to all relevant teams simultaneously |

### 🧬 Claude (Anthropic) — Synthesis Engine
Claude `claude-opus-4-5` receives signals from all 3 agents + Cognee memory context and finds **non-obvious cross-domain correlations** invisible to any single tool.

**Example synthesis:**
- GTM: Competitor raised prices 15%
- Finance: Competitor missed revenue targets  
- Security: Competitor's CISO resigned
- **→ Claude: "Competitor in distress — attack window open. Their customers are evaluating alternatives."**

---

## Quick Start

### 1. Clone & configure
```bash
git clone https://github.com/your-username/sentinel-ai
cd sentinel-ai
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Run locally (development)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/run` | POST | Trigger full agent sweep |
| `GET /api/signals` | GET | List detected signals |
| `GET /api/insights` | GET | List synthesis insights |
| `GET /api/watchlist` | GET | Get monitored entities |
| `POST /api/watchlist` | POST | Add entity to watchlist |
| `POST /api/webhooks/triggerware` | POST | TriggerWare callback |
| `WS /ws` | WebSocket | Real-time agent updates |

### Run Request
```json
{
  "competitors": ["hubspot.com", "salesforce.com"],
  "customers": ["acme-corp", "globex"],
  "vendors": ["okta", "aws", "stripe"]
}
```

---

## Prize Track Alignment

| Track | How Sentinel Qualifies |
|-------|----------------------|
| **GTM Intelligence** | SERP + Scraper API monitors competitor pricing, job postings, G2 reviews → auto-updates CRM via TriggerWare |
| **Finance & Market Intelligence** | Real-time layoff/leadership monitoring → churn risk scoring → CS alerts |
| **Security & Compliance** | CISA feed + vendor breach monitoring → incident tickets + customer notifications |
| **Best Use of Bright Data** | All 5 Bright Data tools used across all 3 agents |
| **Best Use of Featherless AI** | 4 different open-source models, task-routed per agent |
| **Best Use of TriggerWare.ai** | 4 automated workflow types triggered by agent signals |
| **Best Use of AI/ML API** | Claude synthesis engine + Featherless inference pipeline |
| **Best Use of Kiro** | Entire codebase generated and built using Kiro CLI |

---

## Project Structure

```
sentinel-ai/
├── backend/
│   ├── agents/
│   │   ├── types.py              # Shared Signal, Insight, AgentRunResult types
│   │   ├── gtm_agent.py          # GTM Intelligence Agent
│   │   ├── finance_agent.py      # Finance & Market Agent
│   │   ├── security_agent.py     # Security & Compliance Agent
│   │   ├── synthesis_engine.py   # Claude Cross-Agent Synthesis
│   │   └── orchestrator.py       # Parallel agent runner
│   ├── tools/
│   │   ├── bright_data.py        # All 5 Bright Data integrations
│   │   ├── featherless.py        # Open-source model inference
│   │   ├── cognee.py             # Agent memory (store + recall)
│   │   └── triggerware.py        # Automated workflow triggers
│   ├── main.py                   # FastAPI app + WebSocket
│   ├── database.py               # SQLAlchemy models
│   └── config.py                 # Pydantic settings
├── frontend/
│   └── src/
│       ├── store/sentinel.ts     # Zustand global state
│       ├── hooks/useWebSocket.ts # Real-time WS hook
│       ├── components/           # AgentCard, InsightCard, SignalFeed, RunPanel
│       └── pages/Dashboard.tsx   # Main dashboard
├── docker-compose.yml
└── .env.example
```

---

*Built with ❤️ using Kiro CLI at the hackathon.*
