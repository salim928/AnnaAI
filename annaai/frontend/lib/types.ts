export type RunStatus = 'running' | 'completed' | 'failed'
export type DraftStatus = 'draft' | 'approved' | 'published' | 'rejected'
export type DraftType = 'blog_post' | 'instagram_post' | 'email'

export interface Organization {
  id: string
  name: string
  website_url: string | null
  industry: string | null
  brand_voice: string | null
  plan: 'free' | 'pro' | 'business'
  onboarding_complete: boolean
  onboarding_step: number
  created_at: string
}

export interface AgentRun {
  id: string
  org_id: string
  status: RunStatus
  run_type: string
  summary: string | null
  error_message: string | null
  started_at: string
  completed_at: string | null
}

export interface ContentDraft {
  id: string
  org_id: string
  run_id: string | null
  type: DraftType
  title: string | null
  body: string | null
  meta_description: string | null
  image_url: string | null
  topic: string | null
  keywords: string[]
  status: DraftStatus
  rejection_reason: string | null
  platform_url: string | null
  performance_label: 'high_performer' | 'average' | 'low_performer' | null
  created_at: string
  updated_at: string
}

export interface RunStats {
  total_runs: number
  successful_runs: number
  failed_runs: number
  total_drafts: number
  published_drafts: number
  avg_duration_seconds: number
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface OnboardingStatus {
  onboarding_complete: boolean
  onboarding_step: number
  total_steps: number
  current_step_name: string | null
}
