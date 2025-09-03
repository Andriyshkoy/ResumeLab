import { useSyncExternalStore } from 'react'

type AuthState = {
  token: string | null
  userEmail: string | null
  expiresAt: number | null
}

const STORAGE_KIND = (import.meta.env.VITE_AUTH_STORAGE || 'local').toLowerCase()
const storage: Storage = STORAGE_KIND === 'session' ? sessionStorage : localStorage
const KEY = 'auth_state'

let state: AuthState = load()
const listeners = new Set<() => void>()

function load(): AuthState {
  try {
    const raw = storage.getItem(KEY)
    if (!raw) return { token: null, userEmail: null, expiresAt: null }
    const parsed = JSON.parse(raw) as AuthState
    return parsed
  } catch {
    return { token: null, userEmail: null, expiresAt: null }
  }
}

function persist() {
  try {
    storage.setItem(KEY, JSON.stringify(state))
  } catch {}
}

function notify() {
  for (const cb of listeners) cb()
}

export function getToken() {
  return state.token
}

export function setAuth(token: string, expiresIn: number, userEmail: string) {
  const expiresAt = Date.now() + expiresIn * 1000
  state = { token, expiresAt, userEmail }
  persist()
  notify()
}

export function clearAuth() {
  state = { token: null, expiresAt: null, userEmail: null }
  try {
    storage.removeItem(KEY)
  } catch {}
  notify()
}

export function useAuth() {
  const snapshot = () => state
  const subscribe = (cb: () => void) => {
    listeners.add(cb)
    return () => listeners.delete(cb)
  }
  const s = useSyncExternalStore(subscribe, snapshot, snapshot)
  const isAuthed = Boolean(s.token && (!s.expiresAt || Date.now() < s.expiresAt))
  return {
    token: s.token,
    userEmail: s.userEmail,
    expiresAt: s.expiresAt,
    isAuthed,
    logout: clearAuth,
  }
}

