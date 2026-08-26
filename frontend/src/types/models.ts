export type Resource = {
  id: string
  service: string
  resource_type: string
  name: string | null
  arn: string | null
  region: string | null
  status: string | null
  metadata: Record<string, unknown>
  raw: Record<string, unknown>
  origin?: string
  relationships?: Relationship[]
}

export type Relationship = {
  source: string
  target: string
  relationship: string
  confidence: number
  source_field: string | null
}

export type Inventory = {
  connected: boolean
  timestamp: string
  services: Record<string, number>
  total_resources: number
  total_relationships: number
  errors: { service: string; message: string }[]
  unsupported: string[]
}

export type Health = {
  status: string
  floci_connected: boolean
  endpoint: string
  region: string
  last_success_at: string | null
  last_error: string | null
}

export type GraphNode = {
  id: string
  type: string
  data: {
    label: string
    service: string
    resource_type: string
    status?: string | null
    name?: string | null
  }
}

export type GraphEdge = {
  id: string
  source: string
  target: string
  label: string
  data: {
    confidence: number
    relationship: string
    source_field: string | null
  }
}

export type GraphPayload = {
  nodes: GraphNode[]
  edges: GraphEdge[]
  errors: { service: string; message: string }[]
}

export type ResourcePage = {
  items: Resource[]
  total: number
  page: number
  page_size: number
}
