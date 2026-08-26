import { GraphCanvas } from '../components/graph/GraphCanvas'
import { EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { useInfraStore } from '../stores/infrastructure'

export function InfrastructurePage() {
  const graph = useInfraStore((s) => s.graph)
  const loading = useInfraStore((s) => s.loading)
  const error = useInfraStore((s) => s.error)

  if (loading && !graph) return <Skeleton className="h-[420px]" />
  if (error && !graph) return <ErrorState message={error} />
  if (!graph || graph.nodes.length === 0) {
    return (
      <EmptyState
        title="No graph yet"
        body="When Floci has resources, they will appear here with detected relationships."
      />
    )
  }

  return (
    <div className="space-y-3">
      <div>
        <h1 className="text-2xl font-semibold">Infrastructure</h1>
        <p className="text-sm text-[var(--muted)]">
          Confirmed edges are solid. Inferred edges (confidence &lt; 0.9) are dashed.
        </p>
      </div>
      <GraphCanvas graph={graph} />
    </div>
  )
}
