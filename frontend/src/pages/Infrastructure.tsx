import { GraphCanvas } from '../components/graph/GraphCanvas'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { useInfraStore } from '../stores/infrastructure'

export function InfrastructurePage() {
  const graph = useInfraStore((s) => s.graph)
  const loading = useInfraStore((s) => s.loading)
  const error = useInfraStore((s) => s.error)
  const reconnect = useInfraStore((s) => s.reconnect)

  if (loading && !graph) return <Skeleton className="h-[420px]" />
  if (error && !graph) {
    return (
      <ErrorState
        message={error}
        action={
          <button type="button" className="text-[var(--accent)]" onClick={() => void reconnect()}>
            Reconnect
          </button>
        }
      />
    )
  }
  if (!graph || graph.nodes.length === 0) {
    return (
      <EmptyState
        title="No graph yet"
        body="When Floci has resources, they appear here with confirmed and inferred relationships."
      />
    )
  }

  return (
    <div className="space-y-3">
      <div>
        <div className="page-kicker">Map</div>
        <h1 className="mt-1">Infrastructure</h1>
        <p className="mt-1 text-[var(--muted)]">
          Click a node to inspect it. Solid edges are confirmed; dashed edges are inferred.
        </p>
      </div>
      <GraphCanvas graph={graph} />
    </div>
  )
}
