import { useEffect } from 'react'
import { useSentinelStore } from '../store/sentinel'
import { useWebSocket } from '../hooks/useWebSocket'
import { AgentCard } from '../components/AgentCard'
import { InsightCard } from '../components/InsightCard'
import { SignalFeed } from '../components/SignalFeed'
import { RunPanel } from '../components/RunPanel'

export default function Dashboard() {
  useWebSocket()
  const { signals, insights, agentStatuses, wsConnected, loadInitial } = useSentinelStore()

  useEffect(() => {
    Promise.all([
      fetch('/api/signals?limit=50').then((r) => r.json()),
      fetch('/api/insights?limit=20').then((r) => r.json()),
    ]).then(([sigs, ins]) => loadInitial(sigs, ins)).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-sentinel-900 p-6">
      {/* Header */}
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">
            <span className="text-indigo-400">Sentinel</span> AI
          </h1>
          <p className="text-slate-400 text-sm">Unified GTM · Finance · Security Intelligence</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400' : 'bg-red-500'}`} />
          <span className="text-xs text-slate-400">{wsConnected ? 'Live' : 'Disconnected'}</span>
        </div>
      </header>

      {/* Agent Status Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {Object.values(agentStatuses).map((s) => (
          <AgentCard key={s.agent} status={s} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Run Panel + Signal Feed */}
        <div className="lg:col-span-1 space-y-6">
          <RunPanel />
          <div>
            <h2 className="font-bold text-lg mb-3">📡 Live Signal Feed</h2>
            <SignalFeed signals={signals} />
          </div>
        </div>

        {/* Right: Synthesis Insights */}
        <div className="lg:col-span-2">
          <h2 className="font-bold text-lg mb-3">
            🧠 Cross-Agent Synthesis
            <span className="ml-2 text-xs text-purple-400 font-normal">powered by Claude</span>
          </h2>
          {insights.length === 0 ? (
            <div className="bg-sentinel-800 rounded-xl p-8 text-center border border-slate-700">
              <p className="text-4xl mb-3">🧠</p>
              <p className="text-slate-400">Synthesis insights appear here after agents run.</p>
              <p className="text-slate-500 text-sm mt-1">Claude correlates signals across all 3 domains.</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[800px] overflow-y-auto pr-1">
              {insights.map((i) => <InsightCard key={i.id} insight={i} />)}
            </div>
          )}
        </div>
      </div>

      {/* Tech Stack Footer */}
      <footer className="mt-10 pt-6 border-t border-slate-800 text-center">
        <p className="text-xs text-slate-600">
          Powered by{' '}
          <span className="text-slate-500">Bright Data</span> ·{' '}
          <span className="text-slate-500">Claude (Anthropic)</span> ·{' '}
          <span className="text-slate-500">Featherless AI</span> ·{' '}
          <span className="text-slate-500">Cognee</span> ·{' '}
          <span className="text-slate-500">TriggerWare.ai</span> ·{' '}
          <span className="text-slate-500">Built with Kiro CLI</span>
        </p>
      </footer>
    </div>
  )
}
