import { useState } from 'react'
import { useSentinelStore } from '../store/sentinel'
import { API_BASE } from '../hooks/useWebSocket'

export function RunPanel() {
  const { isRunning, setRunning, updateAgentStatus } = useSentinelStore()
  const [competitors, setCompetitors] = useState('hubspot.com, salesforce.com')
  const [customers, setCustomers] = useState('Acme Corp, Globex')
  const [vendors, setVendors] = useState('Okta, AWS, Stripe')

  const handleRun = async () => {
    setRunning(true)
    ;(['gtm', 'finance', 'security'] as const).forEach((a) =>
      updateAgentStatus({ agent: a, running: true, signal_count: 0, model: '', duration_ms: 0 })
    )
    try {
      await fetch(`${API_BASE}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          competitors: competitors.split(',').map((s) => s.trim()).filter(Boolean),
          customers: customers.split(',').map((s) => s.trim()).filter(Boolean),
          vendors: vendors.split(',').map((s) => s.trim()).filter(Boolean),
        }),
      })
    } catch {
      setRunning(false)
    }
  }

  return (
    <div className="bg-sentinel-800 rounded-xl p-5 border border-slate-700">
      <h2 className="font-bold text-lg mb-1">🚀 Run Intelligence Sweep</h2>
      <p className="text-xs text-slate-500 mb-4">Agents run in parallel — watch signals stream in live</p>
      <div className="space-y-3 mb-4">
        <label className="block">
          <span className="text-xs text-slate-400 uppercase tracking-wider">🎯 Competitors to monitor</span>
          <input value={competitors} onChange={(e) => setCompetitors(e.target.value)}
            className="mt-1 w-full bg-sentinel-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
        </label>
        <label className="block">
          <span className="text-xs text-slate-400 uppercase tracking-wider">📊 Customers (churn risk)</span>
          <input value={customers} onChange={(e) => setCustomers(e.target.value)}
            className="mt-1 w-full bg-sentinel-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
        </label>
        <label className="block">
          <span className="text-xs text-slate-400 uppercase tracking-wider">🛡️ Vendors (security watch)</span>
          <input value={vendors} onChange={(e) => setVendors(e.target.value)}
            className="mt-1 w-full bg-sentinel-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
        </label>
      </div>
      <button onClick={handleRun} disabled={isRunning}
        className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-colors">
        {isRunning ? '⏳ Agents Running...' : '▶ Run All 3 Agents'}
      </button>
      {isRunning && (
        <p className="text-xs text-indigo-400 text-center mt-2 animate-pulse">
          GTM → Finance → Security → Synthesis...
        </p>
      )}
    </div>
  )
}
