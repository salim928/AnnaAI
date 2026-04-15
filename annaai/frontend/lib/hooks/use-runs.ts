'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { AgentRun, Paginated, RunStats } from '@/lib/types'

export function useRuns(page = 1, pageSize = 20) {
  return useQuery<Paginated<AgentRun>>({
    queryKey: ['runs', page, pageSize],
    queryFn: () => api.listRuns(page, pageSize),
  })
}

export function useRunStats() {
  return useQuery<RunStats>({
    queryKey: ['run-stats'],
    queryFn: () => api.runStats(),
  })
}

export function useTriggerRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.triggerRun(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['runs'] })
      qc.invalidateQueries({ queryKey: ['run-stats'] })
    },
  })
}
