import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { serviceLabel, servicesFromInventory } from '../services/catalog'
import { useInfraStore } from '../stores/infrastructure'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { ServiceMark } from '../components/common/ServiceMark'

export function DashboardPage() {
  const inventory = useInfraStore((s) => s.inventory)
  const loading = useInfraStore((s) => s.loading)
  const error = useInfraStore((s) => s.error)
  const health = useInfraStore((s) => s.health)
  const reconnect = useInfraStore((s) => s.reconnect)
  const navigate = useNavigate()
  const [showUnused, setShowUnused] = useState(false)

  if (loading && !inventory) {
    return (
      <div className="grid gap-4 md:grid-cols-4">
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    )
  }

  if (error && !inventory) {
    return (
      <ErrorState
        message={error}
        action={
          <button
            type="button"
            className="rounded bg-[var(--accent)] px-3 py-1 text-sm font-semibold text-black"
            onClick={() => void reconnect()}
          >
            Reconnect
          </button>
        }
      />
    )
  }
  if (!inventory) {
    return (
      <EmptyState
        title="No inventory yet"
        body="Start Floci on port 4566, then reconnect so Explorer can list resources."
        action={
          <button
            type="button"
            className="rounded bg-[var(--accent)] px-3 py-1.5 text-sm font-semibold text-black"
            onClick={() => void reconnect()}
          >
            Reconnect
          </button>
        }
      />
    )
  }

  const serviceCount = Object.keys(inventory.services).length
  const tiles = servicesFromInventory(inventory.services).filter(
    (service) => showUnused || (inventory.services[service] ?? 0) > 0,
  )

  return (
    <div className="space-y-6">
      <div>
        <div className="page-kicker">Overview</div>
        <h1 className="mt-1">Dashboard</h1>
        <p className="mt-1 text-[var(--muted)]">Live Floci inventory, not mock data.</p>
      </div>
      <div className="panel grid gap-0 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Resources" value={inventory.total_resources} />
        <Kpi label="Services" value={serviceCount} />
        <Kpi label="Relationships" value={inventory.total_relationships} />
        <Kpi label="Floci" value={health?.floci_connected ? 'Connected' : 'Disconnected'} last />
      </div>
      <div className="flex items-center justify-between">
        <h2 className="text-[13px] font-medium">Services</h2>
        <label className="flex items-center gap-2 text-[12px] text-[var(--muted)]">
          <input
            type="checkbox"
            checked={showUnused}
            onChange={(e) => setShowUnused(e.target.checked)}
          />
          Show unused
        </label>
      </div>
      {tiles.length === 0 ? (
        <EmptyState
          title="No resources in Floci"
          body="Create resources in the emulator, then use Refresh now."
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {tiles.map((service) => (
            <button
              key={service}
              type="button"
              onClick={() => navigate(`/resources?service=${service}`)}
              className="panel p-5 text-left transition-colors hover:border-[var(--accent)]"
            >
              <div className="flex items-center gap-2 text-[var(--muted)]">
                <ServiceMark service={service} />
                <span className="page-kicker">{serviceLabel(service)}</span>
              </div>
              <div className="mt-3 text-[28px] font-semibold leading-none">
                {inventory.services[service] ?? 0}
              </div>
              <div className="mt-1 text-[12px] text-[var(--muted)]">resources</div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function Kpi({
  label,
  value,
  last,
}: {
  label: string
  value: string | number
  last?: boolean
}) {
  return (
    <div className={`p-5 ${last ? '' : 'border-b border-[var(--line)] sm:border-b-0 lg:border-r'}`}>
      <div className="page-kicker">{label}</div>
      <div className="mt-2 text-[22px] font-semibold">{value}</div>
    </div>
  )
}
