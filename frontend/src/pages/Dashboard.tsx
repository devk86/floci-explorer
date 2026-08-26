import { useNavigate } from 'react-router-dom'
import { serviceLabel, servicesFromInventory } from '../services/catalog'
import { useInfraStore } from '../stores/infrastructure'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'

export function DashboardPage() {
  const inventory = useInfraStore((s) => s.inventory)
  const loading = useInfraStore((s) => s.loading)
  const error = useInfraStore((s) => s.error)
  const health = useInfraStore((s) => s.health)
  const navigate = useNavigate()

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

  if (error && !inventory) return <ErrorState message={error} />
  if (!inventory) {
    return (
      <EmptyState
        title="No inventory yet"
        body="Start Floci on port 4566, then use Reconnect."
      />
    )
  }

  const serviceCount = Object.keys(inventory.services).length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-sm text-[var(--muted)]">Live Floci inventory counts, not mock data.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Total resources" value={inventory.total_resources} />
        <Stat label="Total services" value={serviceCount} />
        <Stat label="Relationships" value={inventory.total_relationships} />
        <Stat
          label="Floci status"
          value={health?.floci_connected ? 'Connected' : 'Disconnected'}
        />
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {servicesFromInventory(inventory.services).map((service) => (
          <button
            key={service}
            type="button"
            onClick={() => navigate(`/resources?service=${service}`)}
            className="rounded border border-[var(--line)] bg-[var(--panel)] p-4 text-left hover:border-[var(--accent)]"
          >
            <div className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {serviceLabel(service)}
            </div>
            <div className="mt-2 text-3xl font-semibold">{inventory.services[service] ?? 0}</div>
            <div className="text-xs text-[var(--muted)]">resources</div>
          </button>
        ))}
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
      <div className="text-xs uppercase tracking-wider text-[var(--muted)]">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  )
}
