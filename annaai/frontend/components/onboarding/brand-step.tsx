'use client'

import { Input, Label, Textarea } from '@/components/ui/input'
import type { OnboardingData } from './wizard'

export function BrandStep({
  data,
  update,
}: {
  data: OnboardingData
  update: (p: Partial<OnboardingData>) => void
}) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Tell Anna about your brand</h2>
        <p className="mt-1 text-sm text-muted">
          You can refine this any time in Settings.
        </p>
      </div>
      <div>
        <Label htmlFor="wizard-name">Company name</Label>
        <Input
          id="wizard-name"
          value={data.name}
          onChange={(e) => update({ name: e.target.value })}
        />
      </div>
      <div>
        <Label htmlFor="wizard-industry">Industry</Label>
        <Input
          id="wizard-industry"
          placeholder="SaaS, e-commerce, agency…"
          value={data.industry}
          onChange={(e) => update({ industry: e.target.value })}
        />
      </div>
      <div>
        <Label htmlFor="wizard-voice">Brand voice (optional)</Label>
        <Textarea
          id="wizard-voice"
          rows={3}
          placeholder="Friendly, direct, slightly witty…"
          value={data.brand_voice}
          onChange={(e) => update({ brand_voice: e.target.value })}
        />
      </div>
    </div>
  )
}
