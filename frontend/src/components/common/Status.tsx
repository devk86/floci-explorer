export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-[var(--panel-2)] ${className}`} />
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded border border-dashed border-[var(--line)] bg-[var(--panel)] px-6 py-10 text-center">
      <div className="font-medium">{title}</div>
      <p className="mt-2 text-sm text-[var(--muted)]">{body}</p>
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded border border-[var(--bad)]/40 bg-[var(--bad)]/10 px-4 py-3 text-sm">
      {message}
    </div>
  )
}

export function Field({ label, value }: { label: string; value: unknown }) {
  if (value === undefined || value === null || value === '') return null
  const text = typeof value === 'object' ? JSON.stringify(value) : String(value)
  return (
    <div className="grid grid-cols-[140px_1fr] gap-3 border-b border-[var(--line)] py-2 text-sm">
      <div className="text-[var(--muted)]">{label}</div>
      <div className="mono break-all">{text}</div>
    </div>
  )
}
