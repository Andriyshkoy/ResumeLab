import { api } from '../../shared/utils/axios'

export type EnqueueImproveResponse = { improvement_id: string; status: 'queued' | 'processing' }
export type ImprovementStatus =
  | 'queued'
  | 'processing'
  | 'done'
  | 'failed'

export type ImprovementDetail = {
  id: string
  resume_id: string
  status: ImprovementStatus
  old_content?: string | null
  new_content?: string | null
  error?: string | null
  applied: boolean
  created_at: string
  started_at?: string | null
  finished_at?: string | null
}

export async function enqueueImprove(resumeId: string) {
  const res = await api.post(`/api/v1/resume/${resumeId}/improve`)
  return res.data as EnqueueImproveResponse
}

export async function getImprovement(id: string) {
  const res = await api.get(`/api/v1/improvements/${id}`)
  return res.data as ImprovementDetail
}

