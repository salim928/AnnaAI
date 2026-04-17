'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardHeader } from '@/components/ui/card'
import { RunsTable } from '@/components/dashboard/runs-table'
import { useRuns, useTriggerRun } from '@/lib/hooks/use-runs'

export default function RunsPage() {
  const [page, setPage] = useState(1)
  const runs = useRuns(page, 20)
  const trigger = useTriggerRun()

  async function onTrigger() {
    try {
      await trigger.mutateAsync()
      toast.success('Anna is running.')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed')
    }
  }

  const hasMore = runs.data?.has_more ?? false

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agent runs</h1>
          <p className="text-sm text-muted">
            History of every daily brief Anna has executed.
          </p>
        </div>
        <Button onClick={onTrigger} disabled={trigger.isPending} className="w-full sm:w-auto">
          {trigger.isPending ? 'Starting…' : 'Trigger run'}
        </Button>
      </div>

      <Card>
        <CardHeader title={`Page ${page}`} />
        <RunsTable runs={runs.data?.items ?? []} loading={runs.isPending} />
        <div className="mt-4 flex justify-end gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Previous
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={!hasMore}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      </Card>
    </div>
  )
}
