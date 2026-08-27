import { useCallback, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Link } from 'react-router-dom'
import type { GraphPayload } from '../../types/models'
import { GraphToolbar } from './GraphToolbar'
import { SERVICE_META, serviceLabel } from '../../services/catalog'
import { layoutGraph } from './layout'
import { nodeTypes } from './ResourceNode'
import { ConfidenceChip, TypeBadge } from '../common/Status'
import { ServiceMark } from '../common/ServiceMark'

type Props = { graph: GraphPayload }

function CanvasInner({ graph }: Props) {
  const { fitView, zoomIn, zoomOut } = useReactFlow()
  const [search, setSearch] = useState('')
  const [service, setService] = useState('')
  const [showRelationships, setShowRelationships] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const [layoutKey, setLayoutKey] = useState(0)

  const { nodes, edges } = useMemo(() => {
    const filteredNodes = graph.nodes.filter((node) => {
      if (service && node.data.service !== service) return false
      if (search) {
        const hay = `${node.data.label} ${node.id} ${node.data.service}`.toLowerCase()
        if (!hay.includes(search.toLowerCase())) return false
      }
      return true
    })
    const ids = new Set(filteredNodes.map((node) => node.id))
    const filteredEdges = showRelationships
      ? graph.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target))
      : []
    const connected = new Set<string>()
    if (selected) {
      connected.add(selected)
      filteredEdges.forEach((edge) => {
        if (edge.source === selected || edge.target === selected) {
          connected.add(edge.source)
          connected.add(edge.target)
        }
      })
    }
    const rfNodes: Node[] = filteredNodes.map((node) => ({
      id: node.id,
      type: 'resource',
      data: node.data,
      position: { x: 0, y: 0 },
      style: selected && !connected.has(node.id) ? { opacity: 0.25 } : undefined,
    }))
    const rfEdges: Edge[] = filteredEdges.map((edge) => {
      const confirmed = edge.data.confidence >= 0.9
      const highlighted = selected
        ? edge.source === selected || edge.target === selected
        : true
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: !confirmed,
        style: {
          stroke: confirmed ? '#6b7c8d' : '#e7c36a',
          strokeDasharray: confirmed ? undefined : '6 4',
          opacity: highlighted ? 1 : 0.15,
        },
        labelStyle: { fill: '#8b9aab', fontSize: 10 },
        labelBgStyle: { fill: '#0a1016', fillOpacity: 0.92 },
      }
    })
    return { nodes: layoutGraph(rfNodes, rfEdges), edges: rfEdges }
  }, [graph, search, service, showRelationships, selected, layoutKey])

  const onNodeClick = useCallback((_: unknown, node: Node) => {
    setSelected(node.id)
  }, [])

  const selectedNode = graph.nodes.find((node) => node.id === selected)
  const relatedEdges = graph.edges.filter(
    (edge) => edge.source === selected || edge.target === selected,
  )

  return (
    <div className="flex h-[calc(100vh-180px)] min-h-[420px] flex-col gap-3">
      <GraphToolbar
        search={search}
        onSearch={setSearch}
        service={service}
        onService={setService}
        showRelationships={showRelationships}
        onToggleRelationships={() => setShowRelationships((v) => !v)}
        onFit={() => void fitView({ padding: 0.2 })}
        onReset={() => setLayoutKey((k) => k + 1)}
        onZoomIn={() => void zoomIn()}
        onZoomOut={() => void zoomOut()}
      />
      <div className="flex min-h-0 flex-1 gap-3">
        <div className="relative min-h-0 min-w-0 flex-1 overflow-hidden rounded-[var(--radius)] border border-[var(--line)] bg-[#070b10]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodeClick={onNodeClick}
            onPaneClick={() => setSelected(null)}
            onEdgeClick={(_, edge) => setSelected(edge.source)}
            fitView
            minZoom={0.2}
            maxZoom={1.6}
            defaultEdgeOptions={{ type: 'smoothstep' }}
          >
            <MiniMap
              pannable
              zoomable
              bgColor="#121a23"
              maskColor="rgba(7, 11, 16, 0.8)"
              nodeStrokeWidth={2}
              nodeColor={(node) => {
                const svc = (node.data as { service?: string } | undefined)?.service
                return SERVICE_META[svc ?? '']?.accent ?? '#8b9aab'
              }}
            />
            <Controls showInteractive={false} />
            <Background color="#1c2835" gap={24} size={0.6} />
          </ReactFlow>
          <div className="pointer-events-none absolute bottom-3 left-3 flex gap-3 rounded-md border border-[var(--line)] bg-[var(--panel)]/95 px-3 py-2 text-[11px] text-[var(--muted)]">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-px w-5 bg-[#6b7c8d]" /> Confirmed
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-px w-5 border-t border-dashed border-[var(--warn)]" /> Inferred
            </span>
          </div>
        </div>
        {selectedNode ? (
          <aside className="flex w-72 shrink-0 flex-col overflow-auto rounded-[var(--radius)] border border-[var(--line)] bg-[var(--panel)] p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <ServiceMark service={selectedNode.data.service} />
                <span className="page-kicker">{serviceLabel(selectedNode.data.service)}</span>
              </div>
              <button
                type="button"
                className="text-[11px] text-[var(--muted)] hover:text-white"
                onClick={() => setSelected(null)}
              >
                Close
              </button>
            </div>
            <div className="mt-2 text-[14px] font-medium">{selectedNode.data.label}</div>
            <div className="mt-1">
              <TypeBadge>{selectedNode.data.resource_type}</TypeBadge>
            </div>
            <div className="mono mt-2 break-all text-[11px] text-[var(--muted)]">{selectedNode.id}</div>
            <Link
              className="mt-3 inline-flex rounded bg-[var(--accent)] px-2.5 py-1 text-center text-[12px] font-semibold text-black"
              to={`/resources/${selectedNode.data.service}/${encodeURIComponent(selectedNode.id)}`}
            >
              Open resource
            </Link>
            <div className="mt-4 text-[11px] font-semibold uppercase tracking-wider text-[var(--muted)]">
              Relationships
            </div>
            <div className="mt-2 space-y-2">
              {relatedEdges.length === 0 && (
                <p className="text-[12px] text-[var(--muted)]">None on this graph filter.</p>
              )}
              {relatedEdges.map((edge) => (
                <div key={edge.id} className="rounded-md border border-[var(--line)] bg-[var(--bg)] px-2 py-1.5">
                  <div className="text-[12px] text-[var(--muted)]">{edge.data.relationship}</div>
                  <div className="mono text-[11px]">
                    {edge.source === selected ? edge.target : edge.source}
                  </div>
                  <ConfidenceChip confidence={edge.data.confidence} />
                </div>
              ))}
            </div>
          </aside>
        ) : null}
      </div>
    </div>
  )
}

export function GraphCanvas({ graph }: Props) {
  return (
    <ReactFlowProvider>
      <CanvasInner graph={graph} />
    </ReactFlowProvider>
  )
}
