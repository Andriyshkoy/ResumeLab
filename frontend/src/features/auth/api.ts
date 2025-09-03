import { api } from '../../shared/utils/axios'

export type LoginRequest = { email: string; password: string }
export type LoginResponse = { access_token: string; expires_in: number; token_type?: string }
export type RegisterRequest = { email: string; password: string }

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await api.post('/api/v1/auth/login', data)
  return res.data
}

export async function register(data: RegisterRequest) {
  const res = await api.post('/api/v1/auth/register', data)
  return res.data
}

