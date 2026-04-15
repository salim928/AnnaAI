'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { OnboardingStatus } from '@/lib/types'

export function useOnboardingStatus() {
  return useQuery<OnboardingStatus>({
    queryKey: ['onboarding-status'],
    queryFn: () => api.onboardingStatus(),
  })
}
