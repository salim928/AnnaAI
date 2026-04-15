'use client'

import { clsx } from 'clsx'
import type { OnboardingData } from './wizard'

const GOALS = [
  { id: 'traffic', label: 'Grow organic traffic' },
  { id: 'leads', label: 'Capture more leads' },
  { id: 'authority', label: 'Build thought leadership' },
  { id: 'social', label: 'Stay active on social' },
  { id: 'seo', label: 'Rank for target keywords' },
  { id: 'email', label: 'Nurture the email list' },
]

export function GoalsStep({
  data,
  update,
}: {
  data: OnboardingData
  update: (p: Partial<OnboardingData>) => void
}) {
  function toggle(id: string) {
    const next = data.goals.includes(id)
      ? data.goals.filter((g) => g !== id)
      : [...data.goals, id]
    update({ goals: next })
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">What should Anna focus on?</h2>
        <p className="mt-1 text-sm text-muted">
          Pick the outcomes that matter most. You can change this later.
        </p>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {GOALS.map((g) => {
          const active = data.goals.includes(g.id)
          return (
            <button
              key={g.id}
              type="button"
              onClick={() => toggle(g.id)}
              className={clsx(
                'rounded-lg border px-4 py-3 text-left text-sm font-medium transition',
                active
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border bg-white hover:border-primary',
              )}
            >
              {g.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
