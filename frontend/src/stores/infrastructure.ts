import { create } from 'zustand'
import type { GraphPayload, Health, Inventory, ResourcePage } from '../types/models'
import * as api from '../services/api'

type InfraState = {
  health: Health | null
  inventory: Inventory | null
  graph: GraphPayload | null
  resources: ResourcePage | null
  loading: boolean
  error: string | null
  lastUpdated: number | null
  paused: boolean
  refreshMs: number
  inFlight: boolean
  setPaused: (paused: boolean) => void
  loadHealth: () => Promise<void>
  loadInventory: (force?: boolean) => Promise<boolean>
  loadGraph: () => Promise<void>
  loadResources: (params?: Record<string, string | number | undefined>) => Promise<void>
  refreshAll: (force?: boolean) => Promise<void>
  reconnect: () => Promise<void>
}

export const useInfraStore = create<InfraState>((set, get) => ({
  health: null,
  inventory: null,
  graph: null,
  resources: null,
  loading: false,
  error: null,
  lastUpdated: null,
  paused: false,
  refreshMs: 5000,
  inFlight: false,
  setPaused: (paused) => set({ paused }),
  loadHealth: async () => {
    const health = await api.getHealth()
    set({ health })
  },
  loadInventory: async (force = false) => {
    const previous = get().inventory
    const inventory = await api.getInventory(force)
    const changed =
      !previous ||
      previous.total_resources !== inventory.total_resources ||
      JSON.stringify(previous.services) !== JSON.stringify(inventory.services)
    set({ inventory, lastUpdated: Date.now(), error: null })
    return changed
  },
  loadGraph: async () => {
    const graph = await api.getGraph()
    set({ graph })
  },
  loadResources: async (params) => {
    const resources = await api.getResources(params ?? {})
    set({ resources })
  },
  refreshAll: async (force = false) => {
    if (get().inFlight) return
    set({ inFlight: true, loading: !get().inventory })
    try {
      await get().loadHealth()
      const changed = await get().loadInventory(force)
      if (changed || force || !get().graph) {
        await get().loadGraph()
      }
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Unable to reach the backend',
        health: get().health
          ? { ...get().health!, floci_connected: false }
          : get().health,
      })
    } finally {
      set({ inFlight: false, loading: false })
    }
  },
  reconnect: async () => {
    const health = await api.reconnect()
    set({ health })
    await get().refreshAll(true)
  },
}))
