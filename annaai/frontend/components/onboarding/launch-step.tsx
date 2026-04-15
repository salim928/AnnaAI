'use client'

import { CheckCircle2 } from 'lucide-react'
import type { OnboardingData } from './wizard'

export function LaunchStep({ data }: { data: OnboardingData }) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Ready to meet Anna?</h2>
        <p className="mt-1 text-sm text-muted">
          Here's what I'll do first — usually takes 3 to 5 minutes.
        </p>
      </div>

      <ul className="space-y-2 text-sm">
        <li className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <span>Crawl and analyze {data.website_url || 'your site'}</span>
        </li>
        <li className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <span>Build a vector memory of your brand voice and offerings</span>
        </li>
        <li className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <span>Scout your industry and identify content opportunities</span>
        </li>
        <li className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <span>Generate your first draft for review</span>
        </li>
      </ul>

      <p className="mt-4 rounded-lg bg-bg p-3 text-xs text-muted">
        You'll be able to approve, edit, or reject everything before it's
        published anywhere.
      </p>
    </div>
  )
}
