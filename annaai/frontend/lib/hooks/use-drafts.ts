'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ContentDraft, DraftStatus, Paginated } from '@/lib/types'

export function useDrafts(status?: DraftStatus, page = 1) {
  return useQuery<Paginated<ContentDraft>>({
    queryKey: ['drafts', status ?? 'all', page],
    queryFn: () => api.listDrafts(status, page),
  })
}

export function useDraft(id: string) {
  return useQuery<ContentDraft>({
    queryKey: ['draft', id],
    queryFn: () => api.getDraft(id),
    enabled: Boolean(id),
  })
}

export function useUpdateDraft(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (patch: Partial<ContentDraft>) => api.updateDraft(id, patch),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['draft', id] })
      qc.invalidateQueries({ queryKey: ['drafts'] })
    },
  })
}

export function useApproveDraft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.approveDraft(id),
    onSuccess: (_d, id) => {
      qc.invalidateQueries({ queryKey: ['draft', id] })
      qc.invalidateQueries({ queryKey: ['drafts'] })
    },
  })
}

export function useRejectDraft() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.rejectDraft(id, reason),
    onSuccess: (_d, { id }) => {
      qc.invalidateQueries({ queryKey: ['draft', id] })
      qc.invalidateQueries({ queryKey: ['drafts'] })
    },
  })
}
