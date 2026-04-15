'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { DraftCard } from '@/components/drafts/draft-card'
import { Skeleton } from '@/components/ui/spinner'
import { useDrafts } from '@/lib/hooks/use-drafts'
import type { DraftStatus } from '@/lib/types'
import { clsx } from 'clsx'

const FILTERS: { label: string; value?: DraftStatus }[] = [
  { label: 'All' },
  { label: 'Pending', value: 'draft' },
  { label: 'Approved', value: 'approved' },
  { label: 'Published', value: 'published' },
  { label: 'Rejected', value: 'rejected' },
]

export default function DraftsPage() {
  const [filter, setFilter] = useState<DraftStatus | undefined>(undefined)
  const drafts = useDrafts(filter, 1)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Drafts</h1>
        <p className="text-sm text-muted">
          Review, edit, and approve everything Anna writes.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.label}
            onClick={() => setFilter(f.value)}
            className={clsx(
              'rounded-full border px-4 py-1.5 text-sm font-medium transition',
              filter === f.value
                ? 'border-primary bg-primary text-white'
                : 'border-border bg-white text-surface hover:border-primary',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {drafts.isPending ? (
        <div className="grid gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : drafts.data && drafts.data.items.length > 0 ? (
        <div className="grid gap-4">
          {drafts.data.items.map((d) => (
            <DraftCard key={d.id} draft={d} />
          ))}
        </div>
      ) : (
        <Card>
          <p className="py-8 text-center text-sm text-muted">
            No drafts here yet.
          </p>
        </Card>
      )}
    </div>
  )
}
