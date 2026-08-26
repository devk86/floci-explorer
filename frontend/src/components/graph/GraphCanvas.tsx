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
import { useNavigate } from 'react-router-dom'
import type { GraphPayload } from '../../types/models'
import { GraphToolbar } from './GraphToolbar'
import { SERVICE_META } from '../../services/catalog'
import { layoutGraph } from './layout'
import { nodeTypes } from './ResourceNode'

type Props = { graph: GraphPayload }

function CanvasInner({ graph }: Props) {
  const navigate = useNavigate()
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
          stroke: confirmed ? '#8b9aab' : '#e7c36a',
          strokeDasharray: confirmed ? undefined : '6 4',
          opacity: highlighted ? 1 : 0.15,
        },
      }
    })
    return { nodes: layoutGraph(rfNodes, rfEdges), edges: rfEdges }
  }, [graph, search, service, showRelationships, selected, layoutKey])

  const onNodeClick = useCallback(
    (_: unknown, node: Node) => {
      setSelected(node.id)
      const [svc, ...rest] = node.id.split(':')
      navigate(`/resources/${svc}/${encodeURIComponent(rest.join(':') || node.id)}`)
    },
    [navigate],
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
      <div className="min-h-0 flex-1 overflow-hidden rounded border border-[var(--line)] bg-[#0a1016]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodeClick={onNodeClick}
          onEdgeClick={(_, edge) => setSelected(edge.source)}
          fitView
          minZoom={0.2}
          maxZoom={1.6}
        >
          <MiniMap
            pannable
            zoomable
            bgColor="#121a23"
            maskColor="rgba(11, 17, 23, 0.75)"
            nodeStrokeWidth={2}
            nodeColor={(node) => {
              const service = (node.data as { service?: string } | undefined)?.service
              return SERVICE_META[service ?? '']?.accent ?? '#8b9aab'
            }}
          />
          <Controls showInteractive={false} />
          <Background gap={18} size={1} />
        </ReactFlow>
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
