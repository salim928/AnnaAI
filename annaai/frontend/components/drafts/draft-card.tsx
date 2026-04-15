import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import type { ContentDraft } from '@/lib/types'

function tone(status: ContentDraft['status']) {
  if (status === 'published') return 'success' as const
  if (status === 'approved') return 'info' as const
  if (status === 'rejected') return 'danger' as const
  return 'default' as const
}

export function DraftCard({ draft }: { draft: ContentDraft }) {
  return (
    <Link href={`/drafts/${draft.id}`} className="block">
      <Card className="transition hover:border-primary">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h3 className="truncate text-base font-semibold">
              {draft.title ?? 'Untitled draft'}
            </h3>
            <p className="mt-1 line-clamp-2 text-sm text-muted">
              {draft.meta_description ?? draft.body?.slice(0, 160) ?? ''}
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted">
              <span className="capitalize">{draft.type.replace('_', ' ')}</span>
              <span>·</span>
              <span>{new Date(draft.created_at).toLocaleDateString()}</span>
              {draft.keywords.slice(0, 3).map((k) => (
                <span key={k} className="rounded bg-bg px-2 py-0.5">
                  {k}
                </span>
              ))}
            </div>
          </div>
          <Badge tone={tone(draft.status)}>{draft.status}</Badge>
        </div>
      </Card>
    </Link>
  )
}
