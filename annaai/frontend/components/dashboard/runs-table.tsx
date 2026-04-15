'use client'

import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/spinner'
import type { AgentRun } from '@/lib/types'

function toneFor(status: AgentRun['status']) {
  if (status === 'completed') return 'success' as const
  if (status === 'failed') return 'danger' as const
  return 'info' as const
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export function RunsTable({
  runs,
  loading,
}: {
  runs: AgentRun[]
  loading?: boolean
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (!runs.length) {
    return (
      <p className="py-8 text-center text-sm text-muted">
        No runs yet. Trigger one above to see Anna in action.
      </p>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead className="bg-bg text-xs uppercase tracking-wide text-muted">
          <tr>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Started</th>
            <th className="px-4 py-3">Summary</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {runs.map((r) => (
            <tr key={r.id} className="hover:bg-bg">
              <td className="px-4 py-3 font-medium capitalize">
                {r.run_type.replace(/_/g, ' ')}
              </td>
              <td className="px-4 py-3">
                <Badge tone={toneFor(r.status)}>{r.status}</Badge>
              </td>
              <td className="px-4 py-3 text-muted">
                {formatDate(r.started_at)}
              </td>
              <td className="max-w-sm truncate px-4 py-3 text-muted">
                <Link href={`/runs#${r.id}`}>{r.summary ?? r.error_message ?? '—'}</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
