'use client'

import { Input, Label } from '@/components/ui/input'
import type { OnboardingData } from './wizard'

export function WebsiteStep({
  data,
  update,
}: {
  data: OnboardingData
  update: (p: Partial<OnboardingData>) => void
}) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Where does Anna start?</h2>
        <p className="mt-1 text-sm text-muted">
          Paste your website URL. Anna will crawl it to learn your tone,
          products, and audience.
        </p>
      </div>
      <div>
        <Label htmlFor="wizard-url">Website URL</Label>
        <Input
          id="wizard-url"
          type="url"
          placeholder="https://yourcompany.com"
          value={data.website_url}
          onChange={(e) => update({ website_url: e.target.value })}
        />
      </div>
    </div>
  )
}
