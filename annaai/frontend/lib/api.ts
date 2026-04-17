import type {
  AgentRun,
  ContentDraft,
  DraftStatus,
  OnboardingStatus,
  Paginated,
  RunStats,
} from '@/lib/types'
import { createBrowserSupabase } from '@/lib/supabase/client'

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

async function authHeader(): Promise<Record<string, string>> {
  const supabase = createBrowserSupabase()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return session?.access_token
    ? { Authorization: `Bearer ${session.access_token}` }
    : {}
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const auth = await authHeader()
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...auth,
      ...(init.headers ?? {}),
    },
    credentials: 'include',
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export const api = {
  // --- Onboarding ---------------------------------------------------------
  onboardingStatus: () =>
    request<OnboardingStatus>('/api/onboarding/status'),

  startOnboarding: (body: {
    website_url: string
    name?: string
    industry?: string
  }) =>
    request<{ status: string; message: string }>('/api/onboarding', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  // --- Runs ---------------------------------------------------------------
  listRuns: (page = 1, pageSize = 20) =>
    request<Paginated<AgentRun>>(
      `/api/runs?page=${page}&page_size=${pageSize}`,
    ),

  runStats: () => request<RunStats>('/api/runs/stats'),

  triggerRun: () =>
    request<{ status: string; message: string }>('/api/runs/trigger', {
      method: 'POST',
    }),

  // --- Drafts -------------------------------------------------------------
  listDrafts: (status?: DraftStatus, page = 1, pageSize = 20) => {
    const qs = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })
    if (status) qs.set('status', status)
    return request<Paginated<ContentDraft>>(`/api/drafts?${qs.toString()}`)
  },

  getDraft: (id: string) =>
    request<ContentDraft>(`/api/drafts/${id}`),

  updateDraft: (id: string, body: Partial<ContentDraft>) =>
    request<ContentDraft>(`/api/drafts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  approveDraft: (id: string) =>
    request<ContentDraft>(`/api/drafts/${id}/approve`, { method: 'POST' }),

  rejectDraft: (id: string, reason: string) =>
    request<ContentDraft>(
      `/api/drafts/${id}/reject?reason=${encodeURIComponent(reason)}`,
      { method: 'POST' },
    ),

  // --- Chat streaming -----------------------------------------------------
  streamChat: async (
    message: string,
    history: { role: string; content: string }[],
    onDelta: (text: string) => void,
  ): Promise<void> => {
    const auth = await authHeader()
    const res = await fetch(`${BACKEND_URL}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...auth,
      },
      body: JSON.stringify({ message, history }),
    })
    if (!res.ok || !res.body) {
      throw new Error(`chat stream failed: ${res.status}`)
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() ?? ''
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        const payload = trimmed.slice(5).trim()
        if (payload === '[DONE]') return
        try {
          const parsed = JSON.parse(payload)
          if (parsed.delta) onDelta(parsed.delta)
        } catch {
          // ignore keep-alives
        }
      }
    }
  },

  // --- Integrations -------------------------------------------------------
  listIntegrations: () => request<{ connected: unknown[] }>('/api/integrations'),

  connectWordPress: (body: {
    wp_url: string
    wp_username: string
    wp_app_password: string
  }) =>
    request<{ status: string }>('/api/integrations/wordpress/connect', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  googleAuthorize: () =>
    request<{ authorize_url: string }>('/api/integrations/google/authorize'),

  disconnect: (platform: string) =>
    request<{ status: string }>(`/api/integrations/${platform}`, {
      method: 'DELETE',
    }),

  // --- Settings -----------------------------------------------------------
  getSettings: () =>
    request<{
      id: string
      name: string
      website_url: string | null
      industry: string | null
      brand_voice: string | null
      brand_tone: string | null
      target_audience: string | null
      goals: string | null
      notification_email: string | null
      plan: string
      onboarding_complete: boolean
      onboarding_step: number
      created_at: string
    }>('/api/settings'),

  updateSettings: (body: Record<string, string | null>) =>
    request<Record<string, unknown>>('/api/settings', {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  deleteAccount: () =>
    request<{ status: string }>('/api/settings/account', {
      method: 'DELETE',
    }),

  // --- Billing ------------------------------------------------------------
  listPlans: () =>
    request<
      Array<{
        key: string
        name: string
        price_ghs: number
        interval: string
      }>
    >('/api/billing/plans'),

  currentPlan: () => request<{ plan: string }>('/api/billing/current'),

  startCheckout: (plan: 'pro' | 'business') =>
    request<{ authorization_url: string; reference: string }>(
      '/api/billing/checkout',
      {
        method: 'POST',
        body: JSON.stringify({ plan }),
      },
    ),
}
