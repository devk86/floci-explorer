import { Pause, Play, RefreshCw } from 'lucide-react'
import { useInfraStore } from '../../stores/infrastructure'

function formatTime(ts: number | null) {
  if (!ts) return '—'
  return new Date(ts).toLocaleTimeString()
}

export function TopBar() {
  const health = useInfraStore((s) => s.health)
  const paused = useInfraStore((s) => s.paused)
  const setPaused = useInfraStore((s) => s.setPaused)
  const refreshAll = useInfraStore((s) => s.refreshAll)
  const reconnect = useInfraStore((s) => s.reconnect)
  const lastUpdated = useInfraStore((s) => s.lastUpdated)
  const connected = health?.floci_connected

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--line)] bg-[var(--panel)]/90 px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-3">
        <span
          className={`h-2.5 w-2.5 rounded-full ${connected ? 'bg-[var(--ok)]' : 'bg-[var(--bad)]'}`}
          title={connected ? 'Floci connected' : 'Floci disconnected'}
        />
        <div>
          <div className="text-sm font-semibold">
            {connected ? 'FLOCI CONNECTED' : 'FLOCI DISCONNECTED'}
          </div>
          <div className="text-xs text-[var(--muted)]">
            {health?.endpoint ?? 'endpoint unknown'} · {health?.region ?? 'region unknown'}
          </div>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
        <span>Last updated: {formatTime(lastUpdated)}</span>
        <button
          type="button"
          className="rounded border border-[var(--line)] px-2 py-1 hover:text-white"
          onClick={() => setPaused(!paused)}
        >
          {paused ? (
            <span className="inline-flex items-center gap-1">
              <Play className="h-3 w-3" /> Resume
            </span>
          ) : (
            <span className="inline-flex items-center gap-1">
              <Pause className="h-3 w-3" /> Pause
            </span>
          )}
        </button>
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded border border-[var(--line)] px-2 py-1 hover:text-white"
          onClick={() => void refreshAll(true)}
        >
          <RefreshCw className="h-3 w-3" /> Refresh now
        </button>
        <button
          type="button"
          className="rounded bg-[var(--accent)] px-2 py-1 font-medium text-black"
          onClick={() => void reconnect()}
        >
          Reconnect
        </button>
      </div>
    </header>
  )
}
