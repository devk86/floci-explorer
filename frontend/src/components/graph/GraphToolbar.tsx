import { Maximize2, RotateCcw, Search, ZoomIn, ZoomOut } from 'lucide-react'
import { ALL_SERVICES, serviceLabel } from '../../services/catalog'

type Props = {
  search: string
  onSearch: (value: string) => void
  service: string
  onService: (value: string) => void
  showRelationships: boolean
  onToggleRelationships: () => void
  onFit: () => void
  onReset: () => void
  onZoomIn: () => void
  onZoomOut: () => void
}

export function GraphToolbar(props: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded border border-[var(--line)] bg-[var(--panel)] p-2">
      <label className="relative">
        <Search className="absolute left-2 top-2 h-4 w-4 text-[var(--muted)]" />
        <input
          value={props.search}
          onChange={(e) => props.onSearch(e.target.value)}
          placeholder="Search resources"
          className="w-52 rounded border border-[var(--line)] bg-[var(--bg)] py-1.5 pl-8 pr-2 text-sm"
        />
      </label>
      <select
        value={props.service}
        onChange={(e) => props.onService(e.target.value)}
        className="rounded border border-[var(--line)] bg-[var(--bg)] px-2 py-1.5 text-sm"
      >
        <option value="">All services</option>
        {ALL_SERVICES.map((service) => (
          <option key={service} value={service}>
            {serviceLabel(service)}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={props.onToggleRelationships}
        className="rounded border border-[var(--line)] px-2 py-1.5 text-sm"
      >
        {props.showRelationships ? 'Hide relationships' : 'Show relationships'}
      </button>
      <button type="button" onClick={props.onZoomIn} className="rounded border border-[var(--line)] p-1.5" title="Zoom in">
        <ZoomIn className="h-4 w-4" />
      </button>
      <button type="button" onClick={props.onZoomOut} className="rounded border border-[var(--line)] p-1.5" title="Zoom out">
        <ZoomOut className="h-4 w-4" />
      </button>
      <button type="button" onClick={props.onFit} className="rounded border border-[var(--line)] p-1.5" title="Fit view">
        <Maximize2 className="h-4 w-4" />
      </button>
      <button type="button" onClick={props.onReset} className="rounded border border-[var(--line)] p-1.5" title="Reset layout">
        <RotateCcw className="h-4 w-4" />
      </button>
    </div>
  )
}
