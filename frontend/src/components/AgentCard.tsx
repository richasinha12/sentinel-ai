import { clsx } from 'clsx'
import type { AgentStatus } from '../store/sentinel'

const AGENT_META = {
  gtm: { label: 'GTM Intelligence', icon: '🎯', color: 'border-indigo-500' },
  finance: { label: 'Finance & Market', icon: '📊', color: 'border-emerald-500' },
  security: { label: 'Security & Compliance', icon: '🛡️', color: 'border-red-500' },
  synthesis: { label: 'Cross-Agent Synthesis', icon: '🧠', color: 'border-purple-500' },
}

export function AgentCard({ status }: { status: AgentStatus }) {
  const meta = AGENT_META[status.agent]
  return (
    <div className={clsx('bg-sentinel-800 border-l-4 rounded-lg p-4', meta.color)}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-lg">{meta.icon}</span>
        {status.running && (
          <span className="text-xs text-indigo-400 animate-pulse">● Running</span>
        )}
      </div>
      <p className="font-semibold text-sm">{meta.label}</p>
      <p className="text-2xl font-bold mt-1">{status.signal_count}</p>
      <p className="text-xs text-slate-400 mt-1">signals detected</p>
      {status.model && (
        <p className="text-xs text-slate-500 mt-2 truncate" title={status.model}>
          via {status.model.split('/').pop()}
        </p>
      )}
    </div>
  )
}
