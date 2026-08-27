import { NavLink, Outlet, useSearchParams } from 'react-router-dom'
import { Box, FileStack, LayoutGrid, Network, Search, X } from 'lucide-react'
import { useMemo } from 'react'
import { useInventory } from '../../hooks/useInventory'
import { useWebSocket } from '../../hooks/useWebSocket'
import { serviceAccent, serviceLabel, servicesFromInventory } from '../../services/catalog'
import { useInfraStore } from '../../stores/infrastructure'
import { useUiStore } from '../../stores/ui'
import { BrandMark } from './BrandMark'
import { TopBar } from './TopBar'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutGrid },
  { to: '/infrastructure', label: 'Infrastructure', icon: Network },
  { to: '/resources', label: 'Resources', icon: Box },
  { to: '/terraform', label: 'Terraform', icon: FileStack },
]

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const [params] = useSearchParams()
  const activeService = params.get('service')
  const inventory = useInfraStore((s) => s.inventory)
  const serviceQuery = useUiStore((s) => s.serviceQuery)
  const setServiceQuery = useUiStore((s) => s.setServiceQuery)

  const services = useMemo(() => {
    const needle = serviceQuery.trim().toLowerCase()
    return servicesFromInventory(inventory?.services).filter((service) => {
      const count = inventory?.services[service] ?? 0
      if (count <= 0) return false
      if (!needle) return true
      return serviceLabel(service).toLowerCase().includes(needle) || service.includes(needle)
    })
  }, [inventory, serviceQuery])

  return (
    <>
      <div className="flex items-center justify-between border-b border-[var(--line)] px-4 py-4">
        <BrandMark />
        {onNavigate ? (
          <button type="button" className="md:hidden" onClick={onNavigate} aria-label="Close navigation">
            <X className="h-4 w-4" />
          </button>
        ) : null}
      </div>
      <nav className="flex flex-col gap-1 p-3">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 text-[13px] ${
                isActive
                  ? 'bg-[var(--panel-2)] text-white shadow-[inset_2px_0_0_var(--accent)]'
                  : 'text-[var(--muted)] hover:text-white'
              }`
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-1 min-h-0 flex-1 overflow-y-auto border-t border-[var(--line)] px-3 py-3">
        <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
          Services
        </div>
        <label className="relative mb-2 block">
          <Search className="absolute left-2 top-2 h-3.5 w-3.5 text-[var(--muted)]" />
          <input
            value={serviceQuery}
            onChange={(e) => setServiceQuery(e.target.value)}
            placeholder="Filter services"
            className="w-full rounded-md border border-[var(--line)] bg-[var(--bg)] py-1.5 pl-7 pr-2 text-[12px]"
          />
        </label>
        <div className="space-y-0.5">
          {services.map((service) => (
            <NavLink
              key={service}
              to={`/resources?service=${service}`}
              onClick={onNavigate}
              className={`flex items-center justify-between rounded-md px-2 py-1.5 text-[13px] hover:bg-[var(--panel-2)] hover:text-white ${
                activeService === service
                  ? 'bg-[var(--panel-2)] text-white shadow-[inset_2px_0_0_var(--accent)]'
                  : 'text-[var(--muted)]'
              }`}
            >
              <span className="flex min-w-0 items-center gap-2">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ background: serviceAccent(service) }}
                />
                <span className="truncate">{serviceLabel(service)}</span>
              </span>
              <span className="mono text-[11px]">{inventory?.services[service] ?? 0}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </>
  )
}

export function AppShell() {
  useInventory(true)
  useWebSocket(true)
  const toasts = useUiStore((s) => s.toasts)
  const dismissToast = useUiStore((s) => s.dismissToast)
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen)

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-[var(--line)] bg-[var(--panel)] md:flex">
        <Sidebar />
      </aside>
      {sidebarOpen ? (
        <div className="fixed inset-0 z-40 md:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            aria-label="Close navigation overlay"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="relative flex h-full w-64 flex-col bg-[var(--panel)] shadow-[var(--shadow)]">
            <Sidebar onNavigate={() => setSidebarOpen(false)} />
          </aside>
        </div>
      ) : null}
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="min-w-0 flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <button
            key={toast.id}
            type="button"
            onClick={() => dismissToast(toast.id)}
            className={`block min-w-[220px] rounded-[var(--radius)] border px-3 py-2 text-left text-[13px] shadow-[var(--shadow)] ${
              toast.tone === 'ok'
                ? 'border-[var(--ok)]/40 bg-[var(--panel)] text-[var(--ok)]'
                : toast.tone === 'bad'
                  ? 'border-[var(--bad)]/40 bg-[var(--panel)] text-[var(--bad)]'
                  : 'border-[var(--line)] bg-[var(--panel)]'
            }`}
          >
            {toast.message}
          </button>
        ))}
      </div>
    </div>
  )
}
