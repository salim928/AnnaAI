'use client'

import { use } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ArrowLeft } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { DraftEditor } from '@/components/drafts/draft-editor'
import { ApprovalControls } from '@/components/drafts/approval-controls'
import { useDraft } from '@/lib/hooks/use-drafts'
import type { ContentDraft } from '@/lib/types'

function tone(status: ContentDraft['status']) {
  if (status === 'published') return 'success' as const
  if (status === 'approved') return 'info' as const
  if (status === 'rejected') return 'danger' as const
  return 'default' as const
}

export default function DraftDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const draft = useDraft(id)

  if (draft.isPending) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (!draft.data) {
    return (
      <p className="text-sm text-muted">Draft not found.</p>
    )
  }

  const d = draft.data

  return (
    <div className="space-y-6">
      <Link
        href="/drafts"
        className="inline-flex items-center gap-1 text-sm text-muted hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to drafts
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{d.title ?? 'Untitled draft'}</h1>
          <div className="mt-2 flex items-center gap-3 text-sm text-muted">
            <Badge tone={tone(d.status)}>{d.status}</Badge>
            <span className="capitalize">{d.type.replace('_', ' ')}</span>
            <span>{new Date(d.created_at).toLocaleString()}</span>
          </div>
        </div>
        <ApprovalControls draft={d} />
      </div>

      {d.image_url ? (
        <Card>
          <CardHeader title="Hero image" />
          <div className="relative h-64 w-full overflow-hidden rounded-lg">
            <Image
              src={d.image_url}
              alt={d.title ?? 'Draft hero'}
              fill
              className="object-cover"
              unoptimized
            />
          </div>
        </Card>
      ) : null}

      <Card>
        <CardHeader title="Content" />
        <DraftEditor draft={d} />
      </Card>
    </div>
  )
}
