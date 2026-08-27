import type { ReactNode } from 'react'

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-[var(--radius)] bg-[var(--panel-2)] ${className}`} />
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string
  body: string
  action?: ReactNode
}) {
  return (
    <div className="panel px-6 py-10 text-center">
      <div className="text-[13px] font-medium">{title}</div>
      <p className="mt-2 text-[var(--muted)]">{body}</p>
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  )
}

export function ErrorState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="rounded-[var(--radius)] border border-[var(--bad)]/40 bg-[var(--bad)]/10 px-4 py-3 text-sm">
      <div>{message}</div>
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  )
}

export function Field({
  label,
  value,
  copy,
}: {
  label: string
  value: unknown
  copy?: boolean
}) {
  if (value === undefined || value === null || value === '') return null
  const text = typeof value === 'object' ? JSON.stringify(value) : String(value)
  return (
    <div className="grid grid-cols-[140px_1fr] items-start gap-3 border-b border-[var(--line)] py-2 text-[13px] last:border-b-0">
      <div className="text-[var(--muted)]">{label}</div>
      <div className="flex min-w-0 items-start gap-2">
        <div className="mono min-w-0 break-all">{text}</div>
        {copy ? <CopyButton text={text} /> : null}
      </div>
    </div>
  )
}

export function CopyButton({ text }: { text: string }) {
  return (
    <button
      type="button"
      className="shrink-0 rounded border border-[var(--line)] px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-[var(--muted)] hover:text-white"
      onClick={() => void navigator.clipboard.writeText(text)}
    >
      Copy
    </button>
  )
}

export function TypeBadge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex rounded-full border border-[var(--line)] bg-[var(--panel-2)] px-2 py-0.5 font-mono text-[11px] text-[var(--muted)]">
      {children}
    </span>
  )
}

export function StatusDot({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${
        ok
          ? 'border-[var(--ok)]/30 bg-[var(--ok)]/10 text-[var(--ok)]'
          : 'border-[var(--bad)]/30 bg-[var(--bad)]/10 text-[var(--bad)]'
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? 'bg-[var(--ok)]' : 'bg-[var(--bad)]'}`} />
      {label}
    </span>
  )
}

export function ConfidenceChip({ confidence }: { confidence: number }) {
  const confirmed = confidence >= 0.9
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide ${
        confirmed
          ? 'bg-[var(--panel-2)] text-[var(--muted)]'
          : 'bg-[var(--warn)]/15 text-[var(--warn)]'
      }`}
    >
      {confirmed ? 'Confirmed' : 'Inferred'} · {confidence.toFixed(1)}
    </span>
  )
}
