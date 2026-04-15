'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { WebsiteStep } from './website-step'
import { BrandStep } from './brand-step'
import { GoalsStep } from './goals-step'
import { LaunchStep } from './launch-step'
import { api } from '@/lib/api'

const STEPS = ['Website', 'Brand', 'Goals', 'Launch'] as const

export interface OnboardingData {
  website_url: string
  name: string
  industry: string
  brand_voice: string
  goals: string[]
}

export function OnboardingWizard() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [data, setData] = useState<OnboardingData>({
    website_url: '',
    name: '',
    industry: '',
    brand_voice: '',
    goals: [],
  })
  const [submitting, setSubmitting] = useState(false)

  const update = (patch: Partial<OnboardingData>) =>
    setData((d) => ({ ...d, ...patch }))

  async function launch() {
    setSubmitting(true)
    try {
      await api.startOnboarding({
        website_url: data.website_url,
        name: data.name || undefined,
        industry: data.industry || undefined,
      })
      toast.success('Anna is analyzing your site. This takes a few minutes.')
      router.push('/dashboard')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Onboarding failed')
    } finally {
      setSubmitting(false)
    }
  }

  const canAdvance =
    (step === 0 && data.website_url.trim().length > 0) ||
    (step === 1 && data.name.trim().length > 0) ||
    step === 2 ||
    step === 3

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        {STEPS.map((label, i) => (
          <div key={label} className="flex flex-1 items-center">
            <div
              className={
                i <= step
                  ? 'flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white'
                  : 'flex h-8 w-8 items-center justify-center rounded-full bg-border text-sm font-semibold text-muted'
              }
            >
              {i + 1}
            </div>
            {i < STEPS.length - 1 ? (
              <div
                className={
                  i < step
                    ? 'mx-2 h-0.5 flex-1 bg-primary'
                    : 'mx-2 h-0.5 flex-1 bg-border'
                }
              />
            ) : null}
          </div>
        ))}
      </div>

      <Card>
        {step === 0 ? <WebsiteStep data={data} update={update} /> : null}
        {step === 1 ? <BrandStep data={data} update={update} /> : null}
        {step === 2 ? <GoalsStep data={data} update={update} /> : null}
        {step === 3 ? <LaunchStep data={data} /> : null}

        <div className="mt-6 flex justify-between">
          <Button
            variant="ghost"
            disabled={step === 0}
            onClick={() => setStep((s) => Math.max(0, s - 1))}
          >
            Back
          </Button>
          {step < STEPS.length - 1 ? (
            <Button
              disabled={!canAdvance}
              onClick={() => setStep((s) => s + 1)}
            >
              Continue
            </Button>
          ) : (
            <Button onClick={launch} disabled={submitting}>
              {submitting ? 'Launching Anna…' : 'Launch Anna'}
            </Button>
          )}
        </div>
      </Card>
    </div>
  )
}
