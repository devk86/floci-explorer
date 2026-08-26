import { NavLink, Outlet, useSearchParams } from 'react-router-dom'
import { Activity, Box, FileStack, LayoutGrid, Network } from 'lucide-react'
import { useInventory } from '../../hooks/useInventory'
import { useWebSocket } from '../../hooks/useWebSocket'
import { CORE_SERVICES, serviceLabel, servicesFromInventory } from '../../services/catalog'
import { useInfraStore } from '../../stores/infrastructure'
import { useUiStore } from '../../stores/ui'
import { TopBar } from './TopBar'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutGrid },
  { to: '/infrastructure', label: 'Infrastructure', icon: Network },
  { to: '/resources', label: 'Resources', icon: Box },
  { to: '/terraform', label: 'Terraform', icon: FileStack },
]

export function AppShell() {
  useInventory(true)
  useWebSocket(true)
  const [params] = useSearchParams()
  const activeService = params.get('service')
  const inventory = useInfraStore((s) => s.inventory)
  const toasts = useUiStore((s) => s.toasts)
  const dismissToast = useUiStore((s) => s.dismissToast)

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 border-r border-[var(--line)] bg-[var(--panel)] md:flex md:flex-col">
        <div className="flex items-center gap-2 border-b border-[var(--line)] px-4 py-4">
          <Activity className="h-5 w-5 text-[var(--accent)]" />
          <div>
            <div className="text-sm font-semibold tracking-[0.14em]">FLOCI EXPLORER</div>
            <div className="text-[11px] uppercase text-[var(--muted)]">emulator console</div>
          </div>
        </div>
        <nav className="flex flex-col gap-1 p-3">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded px-3 py-2 text-sm ${
                  isActive ? 'bg-[var(--panel-2)] text-white' : 'text-[var(--muted)] hover:text-white'
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-2 min-h-0 flex-1 overflow-y-auto border-t border-[var(--line)] px-3 py-3">
          <div className="mb-2 text-[11px] uppercase tracking-wider text-[var(--muted)]">Services</div>
          <div className="space-y-1">
            {servicesFromInventory(inventory?.services)
              .filter((service) => (inventory?.services[service] ?? 0) > 0 || CORE_SERVICES.includes(service as (typeof CORE_SERVICES)[number]))
              .map((service) => (
              <NavLink
                key={service}
                to={`/resources?service=${service}`}
                className={`flex items-center justify-between rounded px-2 py-1 text-sm hover:bg-[var(--panel-2)] hover:text-white ${
                  activeService === service ? 'bg-[var(--panel-2)] text-white' : 'text-[var(--muted)]'
                }`}
              >
                <span>{serviceLabel(service)}</span>
                <span className="mono text-xs">{inventory?.services[service] ?? 0}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="min-w-0 flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
      <div className="fixed bottom-4 right-4 space-y-2">
        {toasts.map((toast) => (
          <button
            key={toast.id}
            type="button"
            onClick={() => dismissToast(toast.id)}
            className="block rounded border border-[var(--line)] bg-[var(--panel)] px-3 py-2 text-sm shadow"
          >
            {toast.message}
          </button>
        ))}
      </div>
    </div>
  )
}
