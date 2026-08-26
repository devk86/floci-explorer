import { useState } from 'react'
import { analyzeTerraform } from '../services/api'
import { ErrorState } from '../components/common/Status'

export function TerraformPage() {
  const [rows, setRows] = useState<
    Array<{ resource: string; presence: string; status: string; differences: unknown[] }>
  >([])
  const [error, setError] = useState<string | null>(null)

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Terraform</h1>
      <p className="text-sm text-[var(--muted)]">
        Optional and read-only. Floci inventory works without a state file.
      </p>
      <input
        type="file"
        accept=".json,.tfstate"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (!file) return
          analyzeTerraform(file)
            .then((data) => {
              setRows(data.rows)
              setError(null)
            })
            .catch((err: unknown) =>
              setError(err instanceof Error ? err.message : 'Unable to parse state'),
            )
        }}
      />
      {error && <ErrorState message={error} />}
      {rows.length > 0 && (
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="text-[var(--muted)]">
              <th className="py-2">Resource</th>
              <th>Presence</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.resource} className="border-t border-[var(--line)]">
                <td className="py-2">{row.resource}</td>
                <td>{row.presence}</td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
