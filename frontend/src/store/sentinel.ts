import { create } from 'zustand'

export type Severity = 'low' | 'medium' | 'high' | 'critical'
export type AgentType = 'gtm' | 'finance' | 'security' | 'synthesis'

export interface Signal {
  id: string
  agent: AgentType
  title: string
  summary: string
  severity: Severity
  source_url?: string
  metadata: Record<string, unknown>
  timestamp: string
}

export interface Insight {
  id: string
  title: string
  narrative: string
  severity: Severity
  recommended_actions: string[]
  affected_domains: AgentType[]
  timestamp: string
}

export interface AgentStatus {
  agent: AgentType
  running: boolean
  signal_count: number
  model: string
  duration_ms: number
}

interface SentinelStore {
  signals: Signal[]
  insights: Insight[]
  agentStatuses: Record<AgentType, AgentStatus>
  isRunning: boolean
  wsConnected: boolean
  setWsConnected: (v: boolean) => void
  setRunning: (v: boolean) => void
  addSignals: (signals: Signal[]) => void
  addInsights: (insights: Insight[]) => void
  updateAgentStatus: (status: Partial<AgentStatus> & { agent: AgentType }) => void
  loadInitial: (signals: Signal[], insights: Insight[]) => void
}

const defaultStatus = (agent: AgentType): AgentStatus => ({
  agent, running: false, signal_count: 0, model: '', duration_ms: 0,
})

export const useSentinelStore = create<SentinelStore>((set) => ({
  signals: [],
  insights: [],
  agentStatuses: {
    gtm: defaultStatus('gtm'),
    finance: defaultStatus('finance'),
    security: defaultStatus('security'),
    synthesis: defaultStatus('synthesis'),
  },
  isRunning: false,
  wsConnected: false,
  setWsConnected: (v) => set({ wsConnected: v }),
  setRunning: (v) => set({ isRunning: v }),
  addSignals: (newSignals) => set((s) => ({ signals: [...newSignals, ...s.signals].slice(0, 500) })),
  addInsights: (newInsights) => set((s) => ({ insights: [...newInsights, ...s.insights].slice(0, 100) })),
  updateAgentStatus: (status) =>
    set((s) => ({
      agentStatuses: {
        ...s.agentStatuses,
        [status.agent]: { ...s.agentStatuses[status.agent], ...status },
      },
    })),
  loadInitial: (signals, insights) => set({ signals, insights }),
}))
