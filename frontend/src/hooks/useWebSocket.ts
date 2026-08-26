import { useEffect, useRef } from 'react'
import { useInfraStore } from '../stores/infrastructure'

export function useWebSocket(enabled = true) {
  const refreshAll = useInfraStore((s) => s.refreshAll)
  const attempt = useRef(0)
  const timer = useRef<number | null>(null)

  useEffect(() => {
    if (!enabled) return
    let socket: WebSocket | null = null
    let stopped = false

    const connect = () => {
      if (stopped) return
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${protocol}://${window.location.host}/ws/infrastructure`
      socket = new WebSocket(url)
      socket.onopen = () => {
        attempt.current = 0
      }
      socket.onmessage = () => {
        void refreshAll(true)
      }
      socket.onclose = () => {
        if (stopped) return
        const delay = Math.min(30000, 1000 * 2 ** attempt.current)
        attempt.current += 1
        timer.current = window.setTimeout(connect, delay)
      }
      socket.onerror = () => undefined
    }

    connect()
    return () => {
      stopped = true
      if (timer.current) window.clearTimeout(timer.current)
      socket?.close()
    }
  }, [enabled, refreshAll])
}
