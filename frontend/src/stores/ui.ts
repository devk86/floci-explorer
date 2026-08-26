import { create } from 'zustand'

type Toast = { id: number; message: string; tone: 'ok' | 'bad' | 'info' }

type UiState = {
  search: string
  serviceFilter: string
  statusFilter: string
  showRelationships: boolean
  toasts: Toast[]
  setSearch: (search: string) => void
  setServiceFilter: (serviceFilter: string) => void
  setStatusFilter: (statusFilter: string) => void
  setShowRelationships: (showRelationships: boolean) => void
  pushToast: (message: string, tone?: Toast['tone']) => void
  dismissToast: (id: number) => void
}

let toastId = 1

export const useUiStore = create<UiState>((set) => ({
  search: '',
  serviceFilter: '',
  statusFilter: '',
  showRelationships: true,
  toasts: [],
  setSearch: (search) => set({ search }),
  setServiceFilter: (serviceFilter) => set({ serviceFilter }),
  setStatusFilter: (statusFilter) => set({ statusFilter }),
  setShowRelationships: (showRelationships) => set({ showRelationships }),
  pushToast: (message, tone = 'info') =>
    set((state) => ({ toasts: [...state.toasts, { id: toastId++, message, tone }] })),
  dismissToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((item) => item.id !== id) })),
}))
