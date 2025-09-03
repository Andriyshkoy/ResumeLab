import { api } from '../../shared/utils/axios'

export type ResumeListItem = { id: string; title: string; created_at: string; updated_at: string }
export type ResumeListResponse = {
  items: ResumeListItem[]
  total: number
  limit: number
  offset: number
}
export type ResumeDetail = { id: string; title: string; content: string; created_at: string; updated_at: string }

export async function listResumes(params: { limit: number; offset: number }) {
  const res = await api.get('/api/v1/resume', { params })
  return res.data as ResumeListResponse
}

export async function getResume(id: string) {
  const res = await api.get(`/api/v1/resume/${id}`)
  return res.data as ResumeDetail
}

export async function createResume(data: { title: string; content: string }) {
  const res = await api.post('/api/v1/resume', data)
  return res.data as ResumeDetail
}

export async function updateResume(id: string, data: { title: string; content: string }) {
  const res = await api.put(`/api/v1/resume/${id}`, data)
  return res.data as ResumeDetail
}

export async function deleteResume(id: string) {
  await api.delete(`/api/v1/resume/${id}`)
}

