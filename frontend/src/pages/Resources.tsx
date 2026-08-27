import { useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { ServiceMark } from '../components/common/ServiceMark'
import { ALL_SERVICES, serviceLabel } from '../services/catalog'
import { useInfraStore } from '../stores/infrastructure'

export function ResourcesPage() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const resources = useInfraStore((s) => s.resources)
  const loadResources = useInfraStore((s) => s.loadResources)
  const error = useInfraStore((s) => s.error)
  const loading = useInfraStore((s) => s.loading)
  const reconnect = useInfraStore((s) => s.reconnect)

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

  const openRow = (serviceName: string, id: string) => {
    navigate(`/resources/${serviceName}/${encodeURIComponent(id)}`)
  }

  return (
    <div className="space-y-4">
      <div>
        <div className="page-kicker">Inventory</div>
        <h1 className="mt-1">Resources</h1>
      </div>
      <div className="flex flex-wrap gap-2">
        <input
          defaultValue={search}
          placeholder="Search name, id, type"
          onKeyDown={(e) => {
            if (e.key === 'Enter') update('search', (e.target as HTMLInputElement).value)
          }}
          className="w-64 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--panel)] px-3 py-2"
        />
        <select
          value={service}
          onChange={(e) => update('service', e.target.value)}
          className="rounded-[var(--radius)] border border-[var(--line)] bg-[var(--panel)] px-2 py-2"
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
          className="rounded-[var(--radius)] border border-[var(--line)] bg-[var(--panel)] px-2 py-2"
        >
          <option value="">All statuses</option>
          {statuses.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      {error && (
        <ErrorState
          message={error}
          action={
            <button type="button" className="text-[var(--accent)]" onClick={() => void reconnect()}>
              Reconnect
            </button>
          }
        />
      )}
      {!resources && loading && <Skeleton className="h-64" />}
      {resources && resources.items.length === 0 && (
        <EmptyState
          title="No resources match these filters"
          body="Clear the search, pick another service, or refresh inventory from Floci."
        />
      )}
      {resources && resources.items.length > 0 && (
        <div className="panel max-h-[70vh] overflow-auto">
          <table className="min-w-full text-left">
            <thead className="sticky top-0 z-10 bg-[var(--panel)] text-[11px] uppercase tracking-wider text-[var(--muted)]">
              <tr>
                <th className="px-4 py-2.5 font-medium">Service</th>
                <th className="px-4 py-2.5 font-medium">Name</th>
                <th className="px-4 py-2.5 font-medium">ID</th>
                <th className="px-4 py-2.5 font-medium">Type</th>
                <th className="px-4 py-2.5 font-medium">Status</th>
                <th className="px-4 py-2.5 font-medium">Region</th>
              </tr>
            </thead>
            <tbody>
              {resources.items.map((item, index) => (
                <tr
                  key={item.id}
                  tabIndex={0}
                  className={`cursor-pointer border-t border-[var(--line)] hover:bg-[var(--panel-2)] focus:bg-[var(--panel-2)] focus:outline-none ${
                    index % 2 === 1 ? 'bg-[var(--bg)]/40' : ''
                  }`}
                  onClick={() => openRow(item.service, item.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') openRow(item.service, item.id)
                  }}
                >
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-2">
                      <ServiceMark service={item.service} size={18} />
                      {serviceLabel(item.service)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">{item.name ?? '—'}</td>
                  <td className="mono max-w-[220px] truncate px-4 py-2.5 text-[var(--muted)]" title={item.id}>
                    {item.id}
                  </td>
                  <td className="mono px-4 py-2.5">{item.resource_type}</td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-1.5">
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          (item.status || '').toLowerCase().includes('run') ||
                          (item.status || '').toLowerCase() === 'active' ||
                          (item.status || '').toLowerCase() === 'available'
                            ? 'bg-[var(--ok)]'
                            : 'bg-[var(--muted)]'
                        }`}
                      />
                      {item.status ?? '—'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-[var(--muted)]">{item.region ?? '—'}</td>
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
