import { Handle, Position, type NodeProps } from '@xyflow/react'
import { serviceLabel, SERVICE_META } from '../../services/catalog'

export function ResourceNode({ data, selected }: NodeProps) {
  const payload = data as {
    label: string
    service: string
    resource_type: string
  }
  const accent = SERVICE_META[payload.service]?.accent ?? '#ff9900'
  return (
    <div
      className={`min-w-[180px] rounded border bg-[var(--panel)] px-3 py-2 shadow ${
        selected ? 'border-[var(--accent)]' : 'border-[var(--line)]'
      }`}
      style={{ borderTopWidth: 3, borderTopColor: accent }}
    >
      <Handle type="target" position={Position.Left} />
      <div className="text-[10px] uppercase tracking-wider text-[var(--muted)]">
        {serviceLabel(payload.service)}
      </div>
      <div className="truncate text-sm font-medium">{payload.label}</div>
      <div className="mono text-[11px] text-[var(--muted)]">{payload.resource_type}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}

export const nodeTypes = { resource: ResourceNode }
