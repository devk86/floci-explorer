import { Handle, Position, type NodeProps } from '@xyflow/react'
import { serviceAccent, serviceLabel } from '../../services/catalog'

export function ResourceNode({ data, selected }: NodeProps) {
  const payload = data as {
    label: string
    service: string
    resource_type: string
  }
  const accent = serviceAccent(payload.service)
  return (
    <div
      className={`min-w-[188px] rounded-[8px] border bg-[var(--panel)] py-2 pl-3 pr-3 shadow-[var(--shadow)] ${
        selected ? 'border-[var(--accent)]' : 'border-[var(--line)]'
      }`}
      style={{ borderLeftWidth: 3, borderLeftColor: accent }}
    >
      <Handle type="target" position={Position.Left} />
      <div className="text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)]">
        {serviceLabel(payload.service)}
      </div>
      <div className="truncate text-[13px] font-medium">{payload.label}</div>
      <div className="mono text-[11px] text-[var(--muted)]">{payload.resource_type}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}

export const nodeTypes = { resource: ResourceNode }
