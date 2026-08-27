import { create } from 'zustand'
import type { GraphPayload, Health, Inventory, ResourcePage } from '../types/models'
import * as api from '../services/api'
import { useUiStore } from './ui'

type ResourceQuery = Record<string, string | number | undefined>

type InfraState = {
  health: Health | null
  inventory: Inventory | null
  graph: GraphPayload | null
  resources: ResourcePage | null
  resourceQuery: ResourceQuery
  loading: boolean
  refreshing: boolean
  error: string | null
  lastUpdated: number | null
  forceTick: number
  paused: boolean
  refreshMs: number
  inFlight: boolean
  refreshSeq: number
  setPaused: (paused: boolean) => void
  loadHealth: (seq?: number) => Promise<void>
  loadInventory: (force?: boolean, seq?: number) => Promise<boolean>
  loadGraph: (seq?: number) => Promise<void>
  loadResources: (params?: ResourceQuery, seq?: number) => Promise<void>
  refreshAll: (force?: boolean) => Promise<void>
  reconnect: () => Promise<void>
}

export const useInfraStore = create<InfraState>((set, get) => ({
  health: null,
  inventory: null,
  graph: null,
  resources: null,
  resourceQuery: {},
  loading: false,
  refreshing: false,
  error: null,
  lastUpdated: null,
  forceTick: 0,
  paused: false,
  refreshMs: 5000,
  inFlight: false,
  refreshSeq: 0,
  setPaused: (paused) => set({ paused }),
  loadHealth: async (seq) => {
    const health = await api.getHealth()
    if (seq !== undefined && get().refreshSeq !== seq) return
    set({ health })
  },
  loadInventory: async (force = false, seq) => {
    const previous = get().inventory
    const inventory = await api.getInventory(force)
    if (seq !== undefined && get().refreshSeq !== seq) return false
    const changed =
      !previous ||
      previous.total_resources !== inventory.total_resources ||
      JSON.stringify(previous.services) !== JSON.stringify(inventory.services)
    set({ inventory, lastUpdated: Date.now(), error: null })
    return changed
  },
  loadGraph: async (seq) => {
    const graph = await api.getGraph()
    if (seq !== undefined && get().refreshSeq !== seq) return
    set({ graph })
  },
  loadResources: async (params, seq) => {
    const query = params ?? get().resourceQuery
    const resources = await api.getResources(query)
    if (seq !== undefined && get().refreshSeq !== seq) return
    set({ resources, resourceQuery: query })
  },
  refreshAll: async (force = false) => {
    if (get().inFlight && !force) return
    const seq = get().refreshSeq + 1
    set({
      refreshSeq: seq,
      inFlight: true,
      refreshing: force,
      loading: !get().inventory,
    })
    try {
      await get().loadHealth(seq)
      if (get().refreshSeq !== seq) return
      const changed = await get().loadInventory(force, seq)
      if (get().refreshSeq !== seq) return
      if (force) set({ forceTick: get().forceTick + 1 })
      if (changed || force || !get().graph) {
        await get().loadGraph(seq)
      }
      if (get().refreshSeq !== seq) return
      if (force && Object.keys(get().resourceQuery).length > 0) {
        await get().loadResources(undefined, seq)
      }
      if (force && get().refreshSeq === seq) {
        const total = get().inventory?.total_resources ?? 0
        useUiStore.getState().pushToast(`Inventory updated · ${total} resources`, 'ok')
      }
    } catch (err) {
      if (get().refreshSeq !== seq) return
      set({
        error: err instanceof Error ? err.message : 'Unable to reach the backend',
        health: get().health
          ? { ...get().health!, floci_connected: false }
          : get().health,
      })
      useUiStore.getState().pushToast(
        err instanceof Error ? err.message : 'Unable to reach the backend',
        'bad',
      )
    } finally {
      if (get().refreshSeq === seq) {
        set({ inFlight: false, loading: false, refreshing: false })
      }
    }
  },
  reconnect: async () => {
    const health = await api.reconnect()
    set({ health })
    await get().refreshAll(true)
  },
}))
