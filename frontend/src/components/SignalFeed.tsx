import { SeverityBadge } from './SeverityBadge'
import type { Signal } from '../store/sentinel'
import { formatDistanceToNow } from 'date-fns'

const AGENT_ICONS: Record<string, string> = { gtm: '🎯', finance: '📊', security: '🛡️' }

export function SignalFeed({ signals }: { signals: Signal[] }) {
  if (!signals.length) {
    return <p className="text-slate-500 text-sm text-center py-8">No signals yet. Run agents to start monitoring.</p>
  }
  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
      {signals.map((s) => (
        <div key={s.id} className="bg-sentinel-800 rounded-lg p-3 border border-slate-700/50 hover:border-slate-600 transition-colors">
          <div className="flex items-center gap-2 mb-1">
            <span>{AGENT_ICONS[s.agent] ?? '?'}</span>
            <span className="text-xs text-slate-400 uppercase">{s.agent}</span>
            <SeverityBadge severity={s.severity} />
            <span className="text-xs text-slate-500 ml-auto">
              {formatDistanceToNow(new Date(s.timestamp), { addSuffix: true })}
            </span>
          </div>
          <p className="text-sm font-medium text-white">{s.title}</p>
          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{s.summary}</p>
          {s.source_url && (
            <a href={s.source_url} target="_blank" rel="noopener noreferrer"
               className="text-xs text-indigo-400 hover:underline mt-1 block truncate">
              {s.source_url}
            </a>
          )}
        </div>
      ))}
    </div>
  )
}
