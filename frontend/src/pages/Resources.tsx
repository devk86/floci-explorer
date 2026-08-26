import { useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { ALL_SERVICES, serviceLabel } from '../services/catalog'
import { useInfraStore } from '../stores/infrastructure'

export function ResourcesPage() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const resources = useInfraStore((s) => s.resources)
  const loadResources = useInfraStore((s) => s.loadResources)
  const error = useInfraStore((s) => s.error)
  const loading = useInfraStore((s) => s.loading)

  const service = params.get('service') ?? ''
  const search = params.get('search') ?? ''
  const status = params.get('status') ?? ''
  const page = Number(params.get('page') ?? '1')

  useEffect(() => {
    void loadResources({
      service: service || undefined,
      search: search || undefined,
      status: status || undefined,
      page,
      page_size: 25,
    })
  }, [service, search, status, page, loadResources])

  const statuses = useMemo(() => {
    const values = new Set((resources?.items ?? []).map((item) => item.status).filter(Boolean))
    return [...values] as string[]
  }, [resources])

  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    if (key !== 'page') next.set('page', '1')
    setParams(next)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Resources</h1>
      <div className="flex flex-wrap gap-2">
        <input
          defaultValue={search}
          placeholder="Search name, id, type"
          onKeyDown={(e) => {
            if (e.key === 'Enter') update('search', (e.target as HTMLInputElement).value)
          }}
          className="w-64 rounded border border-[var(--line)] bg-[var(--panel)] px-3 py-2 text-sm"
        />
        <select
          value={service}
          onChange={(e) => update('service', e.target.value)}
          className="rounded border border-[var(--line)] bg-[var(--panel)] px-2 py-2 text-sm"
        >
          <option value="">All services</option>
          {ALL_SERVICES.map((item) => (
            <option key={item} value={item}>
              {serviceLabel(item)}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => update('status', e.target.value)}
          className="rounded border border-[var(--line)] bg-[var(--panel)] px-2 py-2 text-sm"
        >
          <option value="">All statuses</option>
          {statuses.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      {error && <ErrorState message={error} />}
      {!resources && loading && <Skeleton className="h-64" />}
      {resources && resources.items.length === 0 && (
        <EmptyState title="No resources" body="Adjust filters or wait for Floci inventory." />
      )}
      {resources && resources.items.length > 0 && (
        <div className="overflow-x-auto rounded border border-[var(--line)]">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[var(--panel)] text-[var(--muted)]">
              <tr>
                <th className="px-3 py-2 font-medium">Service</th>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Region</th>
              </tr>
            </thead>
            <tbody>
              {resources.items.map((item) => (
                <tr
                  key={item.id}
                  className="cursor-pointer border-t border-[var(--line)] hover:bg-[var(--panel-2)]"
                  onClick={() =>
                    navigate(`/resources/${item.service}/${encodeURIComponent(item.id)}`)
                  }
                >
                  <td className="px-3 py-2">{serviceLabel(item.service)}</td>
                  <td className="px-3 py-2">{item.name ?? item.id}</td>
                  <td className="mono px-3 py-2">{item.resource_type}</td>
                  <td className="px-3 py-2">{item.status ?? '—'}</td>
                  <td className="px-3 py-2">{item.region ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {resources && resources.total > resources.page_size && (
        <div className="flex gap-2 text-sm">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => update('page', String(page - 1))}
            className="rounded border border-[var(--line)] px-2 py-1 disabled:opacity-40"
          >
            Previous
          </button>
          <span className="py-1 text-[var(--muted)]">
            Page {page} of {Math.ceil(resources.total / resources.page_size)}
          </span>
          <button
            type="button"
            disabled={page >= Math.ceil(resources.total / resources.page_size)}
            onClick={() => update('page', String(page + 1))}
            className="rounded border border-[var(--line)] px-2 py-1 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
