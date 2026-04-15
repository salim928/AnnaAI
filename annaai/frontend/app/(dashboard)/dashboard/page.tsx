'use client'

import { Activity, CheckCircle2, FileText, TrendingUp } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardHeader } from '@/components/ui/card'
import { MetricCard } from '@/components/dashboard/metric-card'
import { RunsTable } from '@/components/dashboard/runs-table'
import { TrafficChart } from '@/components/dashboard/traffic-chart'
import { RecentDrafts } from '@/components/dashboard/recent-drafts'
import { useRuns, useRunStats, useTriggerRun } from '@/lib/hooks/use-runs'
import { useDrafts } from '@/lib/hooks/use-drafts'

export default function DashboardPage() {
  const stats = useRunStats()
  const runs = useRuns(1, 5)
  const drafts = useDrafts(undefined, 1)
  const trigger = useTriggerRun()

  const successRate =
    stats.data && stats.data.total_runs > 0
      ? Math.round((stats.data.successful_runs / stats.data.total_runs) * 100)
      : 0

  async function onTrigger() {
    try {
      await trigger.mutateAsync()
      toast.success('Anna is working. Check back in a few minutes.')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to trigger run')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted">
            What your AI crew shipped today.
          </p>
        </div>
        <Button onClick={onTrigger} disabled={trigger.isPending}>
          {trigger.isPending ? 'Starting…' : 'Run Anna now'}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          label="Total runs"
          value={stats.data?.total_runs ?? '—'}
          icon={<Activity className="h-5 w-5" />}
        />
        <MetricCard
          label="Success rate"
          value={stats.data ? `${successRate}%` : '—'}
          icon={<CheckCircle2 className="h-5 w-5" />}
        />
        <MetricCard
          label="Drafts generated"
          value={stats.data?.total_drafts ?? '—'}
          icon={<FileText className="h-5 w-5" />}
        />
        <MetricCard
          label="Published"
          value={stats.data?.published_drafts ?? '—'}
          icon={<TrendingUp className="h-5 w-5" />}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader
            title="Recent runs"
            description="The last five daily briefs."
          />
          <RunsTable runs={runs.data?.items ?? []} loading={runs.isPending} />
        </Card>

        <Card>
          <CardHeader title="Recent drafts" />
          <RecentDrafts
            drafts={drafts.data?.items.slice(0, 5) ?? []}
            loading={drafts.isPending}
          />
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Website traffic"
          description="Sessions from your connected Google Analytics property."
        />
        <TrafficChart data={[]} />
      </Card>
    </div>
  )
}
