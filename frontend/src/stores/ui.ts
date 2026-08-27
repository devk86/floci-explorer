import { create } from 'zustand'

type Toast = { id: number; message: string; tone: 'ok' | 'bad' | 'info' }

type UiState = {
  search: string
  serviceFilter: string
  statusFilter: string
  showRelationships: boolean
  sidebarOpen: boolean
  serviceQuery: string
  toasts: Toast[]
  setSearch: (search: string) => void
  setServiceFilter: (serviceFilter: string) => void
  setStatusFilter: (statusFilter: string) => void
  setShowRelationships: (showRelationships: boolean) => void
  setSidebarOpen: (sidebarOpen: boolean) => void
  setServiceQuery: (serviceQuery: string) => void
  pushToast: (message: string, tone?: Toast['tone']) => void
  dismissToast: (id: number) => void
}

let toastId = 1

export const useUiStore = create<UiState>((set) => ({
  search: '',
  serviceFilter: '',
  statusFilter: '',
  showRelationships: true,
  sidebarOpen: false,
  serviceQuery: '',
  toasts: [],
  setSearch: (search) => set({ search }),
  setServiceFilter: (serviceFilter) => set({ serviceFilter }),
  setStatusFilter: (statusFilter) => set({ statusFilter }),
  setShowRelationships: (showRelationships) => set({ showRelationships }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setServiceQuery: (serviceQuery) => set({ serviceQuery }),
  pushToast: (message, tone = 'info') => {
    const id = toastId++
    set((state) => ({ toasts: [...state.toasts, { id, message, tone }] }))
    window.setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((item) => item.id !== id) }))
    }, 4200)
  },
  dismissToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((item) => item.id !== id) })),
}))
