import { useEffect, useRef } from 'react'
import { useSentinelStore } from '../store/sentinel'

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const { setWsConnected, addSignals, addInsights, updateAgentStatus, setRunning } = useSentinelStore()

  useEffect(() => {
    const connect = () => {
      const socket = new WebSocket(`ws://${window.location.host}/ws`)
      ws.current = socket

      socket.onopen = () => setWsConnected(true)
      socket.onclose = () => {
        setWsConnected(false)
        setTimeout(connect, 3000) // auto-reconnect
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
}
