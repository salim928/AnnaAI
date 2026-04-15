'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/input'
import { Modal } from '@/components/ui/modal'
import type { ContentDraft } from '@/lib/types'
import { useApproveDraft, useRejectDraft } from '@/lib/hooks/use-drafts'

export function ApprovalControls({ draft }: { draft: ContentDraft }) {
  const approve = useApproveDraft()
  const reject = useRejectDraft()
  const [rejectOpen, setRejectOpen] = useState(false)
  const [reason, setReason] = useState('')

  if (draft.status !== 'draft') return null

  async function onApprove() {
    try {
      await approve.mutateAsync(draft.id)
      toast.success('Approved. Queuing for publish.')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Approve failed')
    }
  }

  async function onReject() {
    if (!reason.trim()) {
      toast.error('Please share why so Anna can learn.')
      return
    }
    try {
      await reject.mutateAsync({ id: draft.id, reason })
      toast.success('Feedback captured.')
      setRejectOpen(false)
      setReason('')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Reject failed')
    }
  }

  return (
    <>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={() => setRejectOpen(true)}>
          Reject
        </Button>
        <Button onClick={onApprove} disabled={approve.isPending}>
          {approve.isPending ? 'Approving…' : 'Approve & publish'}
        </Button>
      </div>

      <Modal
        open={rejectOpen}
        onClose={() => setRejectOpen(false)}
        title="Why is this off?"
      >
        <p className="mb-3 text-sm text-muted">
          Anna uses this feedback to improve your brand voice over time.
        </p>
        <Textarea
          rows={4}
          placeholder="E.g. tone is too formal, wrong topic, factually off…"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setRejectOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={onReject}
            disabled={reject.isPending}
          >
            {reject.isPending ? 'Saving…' : 'Submit feedback'}
          </Button>
        </div>
      </Modal>
    </>
  )
}
