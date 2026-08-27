import { Menu, Pause, Play, RefreshCw } from 'lucide-react'
import { useInfraStore } from '../../stores/infrastructure'
import { useUiStore } from '../../stores/ui'
import { StatusDot } from '../common/Status'

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
  const refreshing = useInfraStore((s) => s.refreshing)
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen)
  const connected = health?.floci_connected

  return (
    <header className="relative border-b border-[var(--line)] bg-[var(--panel)]">
      {refreshing ? (
        <div className="absolute inset-x-0 top-0 h-0.5 overflow-hidden bg-[var(--line)]">
          <div className="h-full w-1/3 animate-pulse bg-[var(--accent)]" />
        </div>
      ) : null}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded border border-[var(--line)] p-1.5 md:hidden"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu className="h-4 w-4" />
          </button>
          <StatusDot ok={Boolean(connected)} label={connected ? 'Connected' : 'Disconnected'} />
          <div className="hidden sm:block">
            <div className="mono text-[11px] text-[var(--muted)]">
              {health?.endpoint ?? 'endpoint unknown'}
            </div>
            <div className="text-[11px] text-[var(--muted)]">{health?.region ?? 'region unknown'}</div>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[11px] text-[var(--muted)]">
          <span>Updated {formatTime(lastUpdated)}</span>
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
            className="rounded border border-[var(--line)] px-2 py-1 hover:text-white"
            onClick={() => void reconnect()}
          >
            Reconnect
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded bg-[var(--accent)] px-2.5 py-1 font-semibold text-black"
            onClick={() => void refreshAll(true)}
          >
            <RefreshCw className={`h-3 w-3 ${refreshing ? 'animate-spin' : ''}`} /> Refresh now
          </button>
        </div>
      </div>
    </header>
  )
}
