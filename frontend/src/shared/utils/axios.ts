import axios from 'axios'
import { getToken, clearAuth } from '../../features/auth/auth.store'
import { newRequestId } from './requestId'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  config.headers = config.headers ?? {}
  config.headers['X-Request-ID'] = newRequestId()
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401) {
      clearAuth()
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login'
      }
    }
    return Promise.reject(error)
  },
)

export type ApiError = {
  error?: { code?: string; message?: string }
}

