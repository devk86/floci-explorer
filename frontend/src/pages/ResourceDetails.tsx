import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ConfidenceChip,
  CopyButton,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  TypeBadge,
} from '../components/common/Status'
import { ServiceMark } from '../components/common/ServiceMark'
import { useResource } from '../hooks/useResource'
import { serviceLabel } from '../services/catalog'
import { useInfraStore } from '../stores/infrastructure'
import type { Relationship } from '../types/models'

const TABS = ['Overview', 'Configuration', 'Relationships', 'Raw'] as const
type Tab = (typeof TABS)[number]

function resourceHref(id: string) {
  const service = id.split(':')[0]
  return `/resources/${service}/${encodeURIComponent(id)}`
}

export function ResourceDetailsPage() {
  const { service, resourceId } = useParams()
  const [showSecrets, setShowSecrets] = useState(false)
  const [tab, setTab] = useState<Tab>('Overview')
  const { resource, loading, error } = useResource(service, resourceId, showSecrets)
  const reconnect = useInfraStore((s) => s.reconnect)

  if (loading) return <Skeleton className="h-96" />
  if (error) {
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
  if (!resource) {
    return (
      <EmptyState
        title="Resource not found"
        body="It may have been deleted in Floci. Refresh inventory and try again."
      />
    )
  }

  const meta = resource.metadata
  const rels = resource.relationships ?? []

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <ServiceMark service={resource.service} />
            <span className="page-kicker">{serviceLabel(resource.service)}</span>
            <TypeBadge>{resource.resource_type}</TypeBadge>
          </div>
          <h1 className="mt-2">{resource.name ?? resource.id}</h1>
          <div className="mt-1 flex items-center gap-2 text-[var(--muted)]">
            <span className="mono truncate" title={resource.id}>
              {resource.id}
            </span>
            <CopyButton text={resource.id} />
            {resource.arn ? <CopyButton text={resource.arn} /> : null}
          </div>
        </div>
      </div>
      <div className="flex gap-1 border-b border-[var(--line)]">
        {TABS.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`px-3 py-2 text-[13px] ${
              tab === item
                ? 'border-b-2 border-[var(--accent)] text-white'
                : 'text-[var(--muted)] hover:text-white'
            }`}
          >
            {item}
          </button>
        ))}
      </div>
      {tab === 'Overview' && (
        <section className="panel p-5">
          <Field label="Name" value={resource.name} />
          <Field label="Service" value={resource.service} />
          <Field label="Type" value={resource.resource_type} />
          <Field label="ARN" value={resource.arn} copy />
          <Field label="Region" value={resource.region} />
          <Field label="Status" value={resource.status} />
        </section>
      )}
      {tab === 'Configuration' && (
        <section className="panel p-5">
          {resource.service === 'lambda' && (
            <>
              <Field label="Runtime" value={meta.runtime} />
              <Field label="Handler" value={meta.handler} />
              <Field label="Memory" value={meta.memory} />
              <Field label="Timeout" value={meta.timeout} />
              <Field label="Role" value={meta.role} copy />
            </>
          )}
          {resource.service === 'ec2' && (
            <>
              <Field label="Instance ID" value={meta.instance_id} copy />
              <Field label="Instance type" value={meta.instance_type} />
              <Field label="State" value={resource.status} />
              <Field label="AMI" value={meta.image_id} />
              <Field label="Subnet" value={meta.subnet_id} copy />
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
              <Field label="Queue URL" value={meta.queue_url} copy />
              <Field label="Queue ARN" value={meta.queue_arn} copy />
              <Field label="Attributes" value={meta.attributes} />
            </>
          )}
          {resource.service === 'sns' && (
            <>
              <Field label="Topic ARN" value={resource.arn} copy />
              <Field label="Subscriptions" value={meta.subscriptions} />
            </>
          )}
          {resource.service === 'iam' && (
            <>
              <Field label="Path" value={meta.path} />
              <Field label="User ID" value={meta.user_id} copy />
              <Field label="Create date" value={meta.create_date} />
              <Field label="Tags" value={meta.tags} />
            </>
          )}
          {resource.service === 'lambda' && (
            <div className="mt-4 border-t border-[var(--line)] pt-3">
              <div className="mb-2 flex items-center justify-between">
                <h2 className="text-[13px] font-medium">Environment</h2>
                <label className="text-[12px] text-[var(--muted)]">
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
            </div>
          )}
          {resource.service !== 'lambda' &&
            resource.service !== 'ec2' &&
            resource.service !== 's3' &&
            resource.service !== 'dynamodb' &&
            resource.service !== 'sqs' &&
            resource.service !== 'sns' &&
            resource.service !== 'iam' && (
              <p className="text-[var(--muted)]">See Raw for the full configuration payload.</p>
            )}
        </section>
      )}
      {tab === 'Relationships' && (
        <section className="panel p-5">
          {rels.length === 0 ? (
            <p className="text-[var(--muted)]">No relationships detected for this resource.</p>
          ) : (
            <div className="space-y-2">
              {rels.map((rel) => (
                <RelationshipRow key={`${rel.source}-${rel.target}-${rel.relationship}`} rel={rel} />
              ))}
            </div>
          )}
        </section>
      )}
      {tab === 'Raw' && (
        <section className="panel space-y-4 p-5">
          <div>
            <h2 className="mb-2 text-[13px] font-medium">Metadata</h2>
            <pre className="mono overflow-x-auto rounded-md bg-[var(--bg)] p-3 text-[12px]">
              {JSON.stringify(resource.metadata, null, 2)}
            </pre>
          </div>
          <div>
            <h2 className="mb-2 text-[13px] font-medium">Raw JSON</h2>
            <pre className="mono overflow-x-auto rounded-md bg-[var(--bg)] p-3 text-[12px]">
              {JSON.stringify(resource.raw, null, 2)}
            </pre>
          </div>
        </section>
      )}
    </div>
  )
}

function RelationshipRow({ rel }: { rel: Relationship }) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-md border border-[var(--line)] bg-[var(--bg)] px-3 py-2">
      <Link className="mono text-[var(--accent)] hover:underline" to={resourceHref(rel.source)}>
        {rel.source}
      </Link>
      <span className="text-[var(--muted)]">{rel.relationship}</span>
      <Link className="mono text-[var(--accent)] hover:underline" to={resourceHref(rel.target)}>
        {rel.target}
      </Link>
      <ConfidenceChip confidence={rel.confidence} />
    </div>
  )
}
