'use client'

import { useState } from 'react'
import { clsx } from 'clsx'
import { useQuery, useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Card, CardHeader } from '@/components/ui/card'
import { Input, Label, Textarea } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import { api } from '@/lib/api'

const TABS = ['Profile', 'Brand voice', 'Billing', 'Notifications'] as const
type Tab = (typeof TABS)[number]

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>('Profile')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted">
          Manage your workspace.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              '-mb-px border-b-2 px-4 py-2 text-sm font-medium transition',
              tab === t
                ? 'border-primary text-primary'
                : 'border-transparent text-muted hover:text-ink',
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'Profile' ? <ProfileTab /> : null}
      {tab === 'Brand voice' ? <BrandVoiceTab /> : null}
      {tab === 'Billing' ? <BillingTab /> : null}
      {tab === 'Notifications' ? <NotificationsTab /> : null}
    </div>
  )
}

function ProfileTab() {
  return (
    <Card>
      <CardHeader
        title="Workspace"
        description="Basic details Anna uses when writing."
      />
      <div className="space-y-4">
        <div>
          <Label htmlFor="org-name">Organization name</Label>
          <Input id="org-name" placeholder="Acme Inc." />
        </div>
        <div>
          <Label htmlFor="org-website">Website</Label>
          <Input id="org-website" placeholder="https://acme.com" />
        </div>
        <div>
          <Label htmlFor="org-industry">Industry</Label>
          <Input id="org-industry" placeholder="SaaS, E-commerce…" />
        </div>
        <div className="flex justify-end">
          <Button>Save changes</Button>
        </div>
      </div>
    </Card>
  )
}

function BrandVoiceTab() {
  return (
    <Card>
      <CardHeader
        title="Brand voice"
        description="Describe how you sound. Anna learns more from every draft you approve or reject."
      />
      <Textarea
        rows={8}
        placeholder="Friendly, direct, no jargon. We lean practical over aspirational."
      />
      <div className="mt-4 flex justify-end">
        <Button>Save voice</Button>
      </div>
    </Card>
  )
}

function BillingTab() {
  const current = useQuery({
    queryKey: ['billing-current'],
    queryFn: () => api.currentPlan(),
  })
  const plans = useQuery({
    queryKey: ['billing-plans'],
    queryFn: () => api.listPlans(),
  })
  const checkout = useMutation({
    mutationFn: (plan: 'pro' | 'business') => api.startCheckout(plan),
    onSuccess: (data) => {
      window.location.href = data.authorization_url
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : 'Checkout failed'),
  })

  const active = current.data?.plan ?? 'free'

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title="Current plan"
          action={
            <Badge tone={active === 'free' ? 'default' : 'success'}>
              {active}
            </Badge>
          }
        />
        <p className="text-sm text-muted">
          Upgrade for more daily runs, additional drafts per run, and priority
          queueing.
        </p>
      </Card>

      {plans.isPending ? (
        <Spinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {(plans.data ?? []).map((p) => {
            const isCurrent = p.key === active
            return (
              <Card key={p.key}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-semibold">{p.name}</h3>
                    <p className="mt-1 text-2xl font-bold">
                      GHS {p.price_ghs.toFixed(2)}
                      <span className="text-sm font-normal text-muted">
                        {' '}/ {p.interval}
                      </span>
                    </p>
                  </div>
                  {isCurrent ? <Badge tone="success">Active</Badge> : null}
                </div>
                <div className="mt-4">
                  <Button
                    disabled={isCurrent || checkout.isPending}
                    onClick={() =>
                      checkout.mutate(p.key as 'pro' | 'business')
                    }
                  >
                    {isCurrent ? 'Current plan' : `Upgrade to ${p.name}`}
                  </Button>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

function NotificationsTab() {
  return (
    <Card>
      <CardHeader
        title="Daily brief"
        description="Where Anna sends your morning rundown."
      />
      <div className="space-y-4">
        <div>
          <Label htmlFor="email-to">Send brief to</Label>
          <Input id="email-to" type="email" placeholder="you@company.com" />
        </div>
        <div className="flex justify-end">
          <Button>Save</Button>
        </div>
      </div>
    </Card>
  )
}
