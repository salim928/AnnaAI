'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardHeader } from '@/components/ui/card'
import { Input, Label } from '@/components/ui/input'
import { Modal } from '@/components/ui/modal'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import { api } from '@/lib/api'

interface ConnectedIntegration {
  platform: string
  connected: boolean
  connected_at?: string
}

const AVAILABLE = [
  {
    key: 'wordpress',
    name: 'WordPress',
    description: 'Publish blog posts directly to your WordPress site.',
  },
  {
    key: 'google_analytics',
    name: 'Google Analytics',
    description: 'Let Anna read GA4 sessions and top pages.',
  },
  {
    key: 'google_search_console',
    name: 'Search Console',
    description: 'Pull top keywords and search impressions.',
  },
]

export default function IntegrationsPage() {
  const qc = useQueryClient()
  const list = useQuery<{ connected: ConnectedIntegration[] }>({
    queryKey: ['integrations'],
    queryFn: () =>
      api.listIntegrations() as Promise<{ connected: ConnectedIntegration[] }>,
  })

  const [wpOpen, setWpOpen] = useState(false)
  const [wpUrl, setWpUrl] = useState('')
  const [wpUser, setWpUser] = useState('')
  const [wpPass, setWpPass] = useState('')

  const connectWp = useMutation({
    mutationFn: () =>
      api.connectWordPress({
        wp_url: wpUrl,
        wp_username: wpUser,
        wp_app_password: wpPass,
      }),
    onSuccess: () => {
      toast.success('WordPress connected.')
      setWpOpen(false)
      setWpUrl('')
      setWpUser('')
      setWpPass('')
      qc.invalidateQueries({ queryKey: ['integrations'] })
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : 'Failed'),
  })

  const connectGoogle = useMutation({
    mutationFn: () => api.googleAuthorize(),
    onSuccess: (data) => {
      window.location.href = data.authorize_url
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : 'Failed'),
  })

  const disconnect = useMutation({
    mutationFn: (platform: string) => api.disconnect(platform),
    onSuccess: () => {
      toast.success('Disconnected.')
      qc.invalidateQueries({ queryKey: ['integrations'] })
    },
  })

  function isConnected(platform: string) {
    return list.data?.connected.some(
      (c) => c.platform === platform && c.connected,
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Integrations</h1>
        <p className="text-sm text-muted">
          Connect the tools Anna should read from and publish to.
        </p>
      </div>

      {list.isPending ? (
        <Spinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {AVAILABLE.map((i) => {
            const connected = isConnected(i.key)
            return (
              <Card key={i.key}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-semibold">{i.name}</h3>
                    <p className="mt-1 text-sm text-muted">
                      {i.description}
                    </p>
                  </div>
                  {connected ? (
                    <Badge tone="success">Connected</Badge>
                  ) : (
                    <Badge tone="default">Not connected</Badge>
                  )}
                </div>
                <div className="mt-4 flex gap-2">
                  {connected ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => disconnect.mutate(i.key)}
                    >
                      Disconnect
                    </Button>
                  ) : i.key === 'wordpress' ? (
                    <Button size="sm" onClick={() => setWpOpen(true)}>
                      Connect
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => connectGoogle.mutate()}
                      disabled={connectGoogle.isPending}
                    >
                      Connect with Google
                    </Button>
                  )}
                </div>
              </Card>
            )
          })}
        </div>
      )}

      <Modal
        open={wpOpen}
        onClose={() => setWpOpen(false)}
        title="Connect WordPress"
      >
        <p className="mb-4 text-sm text-muted">
          Create an Application Password in your WordPress admin under Users → Profile.
        </p>
        <div className="space-y-3">
          <div>
            <Label htmlFor="wp-url">Site URL</Label>
            <Input
              id="wp-url"
              placeholder="https://yoursite.com"
              value={wpUrl}
              onChange={(e) => setWpUrl(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="wp-user">Username</Label>
            <Input
              id="wp-user"
              value={wpUser}
              onChange={(e) => setWpUser(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="wp-pass">Application password</Label>
            <Input
              id="wp-pass"
              type="password"
              value={wpPass}
              onChange={(e) => setWpPass(e.target.value)}
            />
          </div>
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setWpOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => connectWp.mutate()}
            disabled={connectWp.isPending || !wpUrl || !wpUser || !wpPass}
          >
            {connectWp.isPending ? 'Connecting…' : 'Connect'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
