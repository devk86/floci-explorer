import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Field, EmptyState, ErrorState, Skeleton } from '../components/common/Status'
import { useResource } from '../hooks/useResource'
import { serviceLabel } from '../services/catalog'

export function ResourceDetailsPage() {
  const { service, resourceId } = useParams()
  const [showSecrets, setShowSecrets] = useState(false)
  const { resource, loading, error } = useResource(service, resourceId, showSecrets)

  if (loading) return <Skeleton className="h-96" />
  if (error) return <ErrorState message={error} />
  if (!resource) {
    return <EmptyState title="Resource not found" body="It may have been deleted in Floci." />
  }

  const meta = resource.metadata

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-wider text-[var(--muted)]">
          {serviceLabel(resource.service)}
        </div>
        <h1 className="text-2xl font-semibold">{resource.name ?? resource.id}</h1>
      </div>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <h2 className="mb-2 font-medium">Overview</h2>
        <Field label="Name" value={resource.name} />
        <Field label="Service" value={resource.service} />
        <Field label="Type" value={resource.resource_type} />
        <Field label="ARN" value={resource.arn} />
        <Field label="Region" value={resource.region} />
        <Field label="Status" value={resource.status} />
      </section>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <h2 className="mb-2 font-medium">Configuration</h2>
        {resource.service === 'lambda' && (
          <>
            <Field label="Runtime" value={meta.runtime} />
            <Field label="Handler" value={meta.handler} />
            <Field label="Memory" value={meta.memory} />
            <Field label="Timeout" value={meta.timeout} />
            <Field label="Role" value={meta.role} />
          </>
        )}
        {resource.service === 'ec2' && (
          <>
            <Field label="Instance ID" value={meta.instance_id} />
            <Field label="Instance type" value={meta.instance_type} />
            <Field label="State" value={resource.status} />
            <Field label="AMI" value={meta.image_id} />
            <Field label="Subnet" value={meta.subnet_id} />
            <Field label="Security groups" value={meta.security_groups} />
            <Field label="Private IP" value={meta.private_ip} />
            <Field label="Public IP" value={meta.public_ip} />
            <Field label="Tags" value={meta.tags} />
          </>
        )}
        {resource.service === 's3' && (
          <>
            <Field label="Bucket name" value={resource.name} />
            <Field label="Region" value={resource.region} />
            <Field label="Creation date" value={meta.creation_date} />
          </>
        )}
        {resource.service === 'dynamodb' && (
          <>
            <Field label="Table name" value={resource.name} />
            <Field label="Status" value={resource.status} />
            <Field label="Partition key" value={meta.partition_key} />
            <Field label="Sort key" value={meta.sort_key} />
            <Field label="Billing mode" value={meta.billing_mode} />
          </>
        )}
        {resource.service === 'sqs' && (
          <>
            <Field label="Queue URL" value={meta.queue_url} />
            <Field label="Queue ARN" value={meta.queue_arn} />
            <Field label="Attributes" value={meta.attributes} />
          </>
        )}
        {resource.service === 'iam' && (
          <>
            <Field label="Path" value={meta.path} />
            <Field label="User ID" value={meta.user_id} />
            <Field label="Create date" value={meta.create_date} />
            <Field label="Tags" value={meta.tags} />
          </>
        )}
      </section>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="font-medium">Environment</h2>
          <label className="text-xs text-[var(--muted)]">
            <input
              type="checkbox"
              className="mr-2"
              checked={showSecrets}
              onChange={(e) => setShowSecrets(e.target.checked)}
            />
            Show secrets
          </label>
        </div>
        <Field label="Variables" value={meta.environment} />
      </section>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <h2 className="mb-2 font-medium">Relationships</h2>
        {(resource.relationships ?? []).length === 0 && (
          <p className="text-sm text-[var(--muted)]">No relationships detected.</p>
        )}
        {(resource.relationships ?? []).map((rel) => (
          <div key={`${rel.source}-${rel.target}-${rel.relationship}`} className="mono py-1 text-sm">
            {rel.source} — {rel.relationship} → {rel.target} ({rel.confidence})
          </div>
        ))}
      </section>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <h2 className="mb-2 font-medium">Metadata</h2>
        <pre className="mono overflow-x-auto text-xs">{JSON.stringify(resource.metadata, null, 2)}</pre>
      </section>
      <section className="rounded border border-[var(--line)] bg-[var(--panel)] p-4">
        <h2 className="mb-2 font-medium">Raw JSON</h2>
        <pre className="mono overflow-x-auto text-xs">{JSON.stringify(resource.raw, null, 2)}</pre>
      </section>
    </div>
  )
}
