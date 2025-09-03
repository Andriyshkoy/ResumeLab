import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/auth.store'

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthed } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!isAuthed) {
      navigate('/auth/login', { replace: true, state: { from: location } })
    }
  }, [isAuthed, navigate, location])

  return <>{isAuthed ? children : null}</>
}
