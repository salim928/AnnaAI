'use client'

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input, Label, Textarea } from '@/components/ui/input'
import type { ContentDraft } from '@/lib/types'
import { useUpdateDraft } from '@/lib/hooks/use-drafts'

export function DraftEditor({ draft }: { draft: ContentDraft }) {
  const [title, setTitle] = useState(draft.title ?? '')
  const [metaDescription, setMetaDescription] = useState(
    draft.meta_description ?? '',
  )
  const [body, setBody] = useState(draft.body ?? '')
  const update = useUpdateDraft(draft.id)

  useEffect(() => {
    setTitle(draft.title ?? '')
    setMetaDescription(draft.meta_description ?? '')
    setBody(draft.body ?? '')
  }, [draft.id, draft.title, draft.meta_description, draft.body])

  async function onSave() {
    try {
      await update.mutateAsync({
        title,
        meta_description: metaDescription,
        body,
      })
      toast.success('Draft saved.')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const editable = draft.status === 'draft'

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="draft-title">Title</Label>
        <Input
          id="draft-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={!editable}
        />
      </div>
      <div>
        <Label htmlFor="draft-meta">Meta description</Label>
        <Textarea
          id="draft-meta"
          rows={2}
          value={metaDescription}
          onChange={(e) => setMetaDescription(e.target.value)}
          disabled={!editable}
        />
      </div>
      <div>
        <Label htmlFor="draft-body">Body</Label>
        <Textarea
          id="draft-body"
          rows={18}
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={!editable}
        />
      </div>
      {editable ? (
        <div className="flex justify-end">
          <Button onClick={onSave} disabled={update.isPending}>
            {update.isPending ? 'Saving…' : 'Save changes'}
          </Button>
        </div>
      ) : null}
    </div>
  )
}
