import { useEffect, useRef } from 'react'
import { useSentinelStore } from '../store/sentinel'

// In production (Vercel), VITE_API_URL = your Railway backend URL
const API_BASE = import.meta.env.VITE_API_URL || ''
const WS_BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace('https://', 'wss://').replace('http://', 'ws://')
  : `ws://${window.location.host}`

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const { setWsConnected, addSignals, addInsights, updateAgentStatus, setRunning } = useSentinelStore()

  useEffect(() => {
    const connect = () => {
      const socket = new WebSocket(`${WS_BASE}/ws`)
      ws.current = socket
      socket.onopen = () => setWsConnected(true)
      socket.onclose = () => {
        setWsConnected(false)
        setTimeout(connect, 3000)
      }
      socket.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === 'agent_done') {
          updateAgentStatus({ agent: msg.agent, running: false, signal_count: msg.signal_count,
                               model: msg.model, duration_ms: msg.duration_ms })
          if (msg.signals?.length) addSignals(msg.signals)
        } else if (msg.type === 'synthesis_done') {
          if (msg.insights?.length) addInsights(msg.insights)
          setRunning(false)
        }
      }
    }
    connect()
    return () => ws.current?.close()
  }, [])

  return API_BASE
}

export { API_BASE }
