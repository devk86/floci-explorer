import { serviceAccent, serviceLabel } from '../../services/catalog'

export function ServiceMark({ service, size = 22 }: { service: string; size?: number }) {
  const accent = serviceAccent(service)
  const letters = serviceLabel(service)
    .replace(/[^A-Za-z0-9]/g, '')
    .slice(0, 2)
    .toUpperCase()
  return (
    <span
      className="inline-flex shrink-0 items-center justify-center rounded font-semibold tracking-wide text-[10px] text-black"
      style={{ width: size, height: size, background: accent }}
      title={serviceLabel(service)}
    >
      {letters}
    </span>
  )
}
