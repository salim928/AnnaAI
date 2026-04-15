'use client'

import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/spinner'
import type { ContentDraft } from '@/lib/types'

function tone(status: ContentDraft['status']) {
  if (status === 'published') return 'success' as const
  if (status === 'approved') return 'info' as const
  if (status === 'rejected') return 'danger' as const
  return 'default' as const
}

export function RecentDrafts({
  drafts,
  loading,
}: {
  drafts: ContentDraft[]
  loading?: boolean
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    )
  }

  if (!drafts.length) {
    return (
      <p className="py-8 text-center text-sm text-muted">
        Drafts will appear here after your next run.
      </p>
    )
  }

  return (
    <ul className="divide-y divide-border">
      {drafts.map((d) => (
        <li key={d.id} className="py-3">
          <Link
            href={`/drafts/${d.id}`}
            className="flex items-start justify-between gap-4 hover:text-primary"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{d.title ?? 'Untitled draft'}</p>
              <p className="mt-1 text-xs text-muted">
                {d.type.replace('_', ' ')} · {new Date(d.created_at).toLocaleDateString()}
              </p>
            </div>
            <Badge tone={tone(d.status)}>{d.status}</Badge>
          </Link>
        </li>
      ))}
    </ul>
  )
}
