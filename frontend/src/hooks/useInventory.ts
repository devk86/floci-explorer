import { useEffect } from 'react'
import { useInfraStore } from '../stores/infrastructure'

export function useInventory(enabled = true) {
  const refreshAll = useInfraStore((s) => s.refreshAll)
  const paused = useInfraStore((s) => s.paused)
  const refreshMs = useInfraStore((s) => s.refreshMs)
  const inventory = useInfraStore((s) => s.inventory)
  const loading = useInfraStore((s) => s.loading)
  const error = useInfraStore((s) => s.error)
  const lastUpdated = useInfraStore((s) => s.lastUpdated)

  useEffect(() => {
    if (!enabled) return
    void refreshAll(true)
  }, [enabled, refreshAll])

  useEffect(() => {
    if (!enabled || paused) return
    const id = window.setInterval(() => {
      void refreshAll(false)
    }, refreshMs)
    return () => window.clearInterval(id)
  }, [enabled, paused, refreshMs, refreshAll])

  return { inventory, loading, error, lastUpdated, refreshAll }
}
