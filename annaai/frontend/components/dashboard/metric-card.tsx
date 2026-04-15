import type { ReactNode } from 'react'
import { Card } from '@/components/ui/card'

export function MetricCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string
  value: string | number
  hint?: string
  icon?: ReactNode
}) {
  return (
    <Card className="flex items-start justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">
          {label}
        </p>
        <p className="mt-2 text-2xl font-bold">{value}</p>
        {hint ? (
          <p className="mt-1 text-xs text-muted">{hint}</p>
        ) : null}
      </div>
      {icon ? (
        <div className="rounded-lg bg-bg p-2 text-primary">
          {icon}
        </div>
      ) : null}
    </Card>
  )
}
