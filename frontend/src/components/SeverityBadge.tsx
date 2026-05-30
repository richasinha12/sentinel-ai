import { clsx } from 'clsx'
import type { Severity } from '../store/sentinel'

const colors: Record<Severity, string> = {
  low: 'bg-slate-700 text-slate-300',
  medium: 'bg-yellow-900 text-yellow-300',
  high: 'bg-orange-900 text-orange-300',
  critical: 'bg-red-900 text-red-300 animate-pulse',
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={clsx('px-2 py-0.5 rounded text-xs font-semibold uppercase', colors[severity])}>
      {severity}
    </span>
  )
}
