import axios from 'axios'
import type {
  GraphPayload,
  Health,
  Inventory,
  Resource,
  ResourcePage,
} from '../types/models'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 60000,
})

export async function getHealth() {
  const { data } = await client.get<Health>('/api/health')
  return data
}

export async function reconnect() {
  const { data } = await client.post<Health>('/api/health/reconnect')
  return data
}

export async function getInventory(refresh = false) {
  const { data } = await client.get<Inventory>('/api/inventory', {
    params: { refresh },
  })
  return data
}

export async function getResources(params: {
  page?: number
  page_size?: number
  search?: string
  status?: string
  service?: string
}) {
  const { data } = await client.get<ResourcePage>('/api/resources', { params })
  return data
}

export async function getResource(
  service: string,
  resourceId: string,
  showSecrets = false,
) {
  const { data } = await client.get<Resource>(
    `/api/resources/${encodeURIComponent(service)}/${encodeURIComponent(resourceId)}`,
    { params: { show_secrets: showSecrets } },
  )
  return data
}

export async function getGraph() {
  const { data } = await client.get<GraphPayload>('/api/graph')
  return data
}

export async function analyzeTerraform(file: File) {
  const body = new FormData()
  body.append('file', file)
  const { data } = await client.post('/api/terraform/analyze', body)
  return data as {
    terraform_resources: number
    rows: Array<{
      resource: string
      service: string
      presence: string
      status: string
      differences: Array<{ field: string; floci: unknown; terraform: unknown }>
    }>
  }
}

export { client }
