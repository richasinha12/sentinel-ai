import { useEffect } from 'react'
import { useSentinelStore } from '../store/sentinel'
import { useWebSocket, API_BASE } from '../hooks/useWebSocket'
import { AgentCard } from '../components/AgentCard'
import { InsightCard } from '../components/InsightCard'
import { SignalFeed } from '../components/SignalFeed'
import { RunPanel } from '../components/RunPanel'

const TRACKS = [
  { emoji: '🎯', label: 'GTM Intelligence', color: 'border-indigo-500 text-indigo-400' },
  { emoji: '📊', label: 'Finance & Market', color: 'border-emerald-500 text-emerald-400' },
  { emoji: '🛡️', label: 'Security & Compliance', color: 'border-red-500 text-red-400' },
  { emoji: '🧠', label: 'Cross-Agent Synthesis', color: 'border-purple-500 text-purple-400' },
]

const TECH = [
  { label: 'Bright Data', sub: 'SERP · Unlocker · Scraper · Browser · MCP', color: 'bg-orange-950 text-orange-300' },
  { label: 'Claude (Anthropic)', sub: 'Cross-agent synthesis engine', color: 'bg-purple-950 text-purple-300' },
  { label: 'Featherless AI', sub: 'Mistral · Llama-3 · Phi-3 · Qwen2', color: 'bg-blue-950 text-blue-300' },
  { label: 'Cognee', sub: 'Agent memory & knowledge graph', color: 'bg-teal-950 text-teal-300' },
  { label: 'TriggerWare.ai', sub: 'CRM · CS alerts · Incident tickets', color: 'bg-yellow-950 text-yellow-300' },
  { label: 'Kiro CLI', sub: 'Custom agents · Smart hooks · Steering', color: 'bg-indigo-950 text-indigo-300' },
]

export default function Dashboard() {
  useWebSocket()
  const { signals, insights, agentStatuses, wsConnected, loadInitial } = useSentinelStore()

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/signals?limit=50`).then((r) => r.json()),
      fetch(`${API_BASE}/api/insights?limit=20`).then((r) => r.json()),
    ]).then(([sigs, ins]) => loadInitial(sigs, ins)).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-sentinel-900 p-4 md:p-6 max-w-7xl mx-auto">

      {/* ── Header ── */}
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">
            <span className="text-indigo-400">Sentinel</span>
            <span className="text-white"> AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            24/7 autonomous intelligence across GTM · Finance · Security
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-xs text-slate-400">{wsConnected ? 'Live' : 'Connecting...'}</span>
        </div>
      </header>

      {/* ── Hero Problem/Solution ── */}
      <div className="bg-gradient-to-r from-indigo-950/60 to-purple-950/40 border border-indigo-800/40 rounded-xl p-5 mb-6">
        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1">
            <p className="text-red-400 font-semibold text-sm mb-1">❌ The Problem</p>
            <p className="text-white font-bold text-lg">Companies pay $13,500+/month across 5+ siloed tools that never talk to each other.</p>
          </div>
          <div className="hidden md:block text-3xl text-slate-600">→</div>
          <div className="flex-1">
            <p className="text-emerald-400 font-semibold text-sm mb-1">✅ The Solution</p>
            <p className="text-white font-bold text-lg">Sentinel replaces all of them for $500/month — and connects the dots between them.</p>
          </div>
        </div>
      </div>

      {/* ── Prize Tracks ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {TRACKS.map((t) => (
          <div key={t.label} className={`border-l-2 ${t.color} bg-sentinel-800 rounded-lg px-3 py-2`}>
            <span className="text-lg">{t.emoji}</span>
            <p className={`text-xs font-semibold mt-1 ${t.color.split(' ')[1]}`}>{t.label}</p>
          </div>
        ))}
      </div>

      {/* ── Agent Status ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {Object.values(agentStatuses).map((s) => (
          <AgentCard key={s.agent} status={s} />
        ))}
      </div>

      {/* ── Main Content ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-1 space-y-6">
          <RunPanel />
          <div>
            <h2 className="font-bold text-base mb-3">📡 Live Signal Feed
              <span className="ml-2 text-xs text-slate-500 font-normal">
                Bright Data SERP · Unlocker · MCP
              </span>
            </h2>
            <SignalFeed signals={signals} />
          </div>
        </div>

        <div className="lg:col-span-2">
          <h2 className="font-bold text-base mb-3">
            🧠 Cross-Agent Synthesis
            <span className="ml-2 text-xs text-purple-400 font-normal">
              Claude finds patterns invisible to any single agent
            </span>
          </h2>
          {insights.length === 0 ? (
            <div className="bg-sentinel-800 rounded-xl p-10 text-center border border-slate-700">
              <p className="text-5xl mb-3">🧠</p>
              <p className="text-white font-semibold mb-1">Click "Run All 3 Agents" to see the magic</p>
              <p className="text-slate-400 text-sm">Claude will correlate signals across GTM + Finance + Security</p>
              <p className="text-slate-500 text-xs mt-2">Example: Competitor raised prices + missed revenue + CISO resigned → Attack window open</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[800px] overflow-y-auto pr-1">
              {insights.map((i) => <InsightCard key={i.id} insight={i} />)}
            </div>
          )}
        </div>
      </div>

      {/* ── Tech Stack ── */}
      <div className="border-t border-slate-800 pt-6">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Partner Technologies</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {TECH.map((t) => (
            <div key={t.label} className={`${t.color} rounded-lg p-2.5`}>
              <p className="font-semibold text-xs">{t.label}</p>
              <p className="text-xs opacity-70 mt-0.5">{t.sub}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-600 text-center mt-4">
          Built entirely with <span className="text-indigo-400">Kiro CLI</span> — custom agents (.kiro/agents/) · smart hooks (.kiro/hooks/) · project steering (.kiro/steering.md)
        </p>
      </div>
    </div>
  )
}
