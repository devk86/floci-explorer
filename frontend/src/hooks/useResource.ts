import { useEffect, useState } from 'react'
import { getResource } from '../services/api'
import type { Resource } from '../types/models'

export function useResource(service?: string, resourceId?: string, showSecrets = false) {
  const [resource, setResource] = useState<Resource | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!service || !resourceId) return
    let cancelled = false
    setLoading(true)
    setError(null)
    getResource(service, resourceId, showSecrets)
      .then((data) => {
        if (!cancelled) setResource(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Resource not found')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [service, resourceId, showSecrets])

  return { resource, loading, error }
}
