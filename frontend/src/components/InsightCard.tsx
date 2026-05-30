import { SeverityBadge } from './SeverityBadge'
import type { Insight } from '../store/sentinel'
import { formatDistanceToNow } from 'date-fns'

const DOMAIN_ICONS: Record<string, string> = { gtm: '🎯', finance: '📊', security: '🛡️' }

export function InsightCard({ insight }: { insight: Insight }) {
  return (
    <div className="bg-gradient-to-br from-purple-950/60 to-sentinel-800 border border-purple-800/50 rounded-xl p-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-purple-400 font-bold text-xs uppercase tracking-wider">🧠 Synthesis</span>
          <div className="flex gap-1">
            {insight.affected_domains.map((d) => (
              <span key={d} title={d}>{DOMAIN_ICONS[d] ?? '?'}</span>
            ))}
          </div>
        </div>
        <SeverityBadge severity={insight.severity} />
      </div>
      <h3 className="font-bold text-white mb-2">{insight.title}</h3>
      <p className="text-slate-300 text-sm mb-4">{insight.narrative}</p>
      {insight.recommended_actions.length > 0 && (
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">Recommended Actions</p>
          <ul className="space-y-1">
            {insight.recommended_actions.map((a, i) => (
              <li key={i} className="text-sm text-slate-200 flex gap-2">
                <span className="text-purple-400">→</span> {a}
              </li>
            ))}
          </ul>
        </div>
      )}
      <p className="text-xs text-slate-500 mt-3">
        {formatDistanceToNow(new Date(insight.timestamp), { addSuffix: true })}
      </p>
    </div>
  )
}
