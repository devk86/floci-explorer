import { useState } from 'react'
import { analyzeTerraform } from '../services/api'
import { EmptyState, ErrorState } from '../components/common/Status'

export function TerraformPage() {
  const [rows, setRows] = useState<
    Array<{ resource: string; presence: string; status: string; differences: unknown[] }>
  >([])
  const [error, setError] = useState<string | null>(null)

  return (
    <div className="space-y-4">
      <div>
        <div className="page-kicker">Drift</div>
        <h1 className="mt-1">Terraform</h1>
        <p className="mt-1 text-[var(--muted)]">
          Optional and read-only. Floci inventory works without a state file.
        </p>
      </div>
      <div className="panel p-5">
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
      </div>
      {error && <ErrorState message={error} />}
      {rows.length === 0 && !error ? (
        <EmptyState
          title="No state uploaded"
          body="Choose a terraform.tfstate file to compare with the current Floci inventory."
        />
      ) : null}
      {rows.length > 0 && (
        <div className="panel overflow-auto">
          <table className="min-w-full text-left">
            <thead className="sticky top-0 bg-[var(--panel)] text-[11px] uppercase tracking-wider text-[var(--muted)]">
              <tr>
                <th className="px-4 py-2.5 font-medium">Resource</th>
                <th className="px-4 py-2.5 font-medium">Presence</th>
                <th className="px-4 py-2.5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr
                  key={row.resource}
                  className={`border-t border-[var(--line)] ${index % 2 === 1 ? 'bg-[var(--bg)]/40' : ''}`}
                >
                  <td className="px-4 py-2.5">{row.resource}</td>
                  <td className="px-4 py-2.5">{row.presence}</td>
                  <td className="px-4 py-2.5">{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
