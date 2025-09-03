import { useState, useRef, useEffect } from 'react'
import { Button, Alert } from 'react-bootstrap'
import { enqueueImprove, getImprovement } from './api'
import { getResume } from '../resumes/api'
import { useQueryClient } from '@tanstack/react-query'

const DEFAULT_INTERVAL = Number(import.meta.env.VITE_POLL_INTERVAL_MS || 1000)
const DEFAULT_TIMEOUT = Number(import.meta.env.VITE_POLL_TIMEOUT_MS || 60000)

export function ImproveButton({ resumeId }: { resumeId: string }) {
  const [status, setStatus] = useState<'idle' | 'running' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const isMounted = useRef(true)
  const queryClient = useQueryClient()

  useEffect(() => () => {
    isMounted.current = false
  }, [])

  const poll = async (improvementId: string) => {
    const start = Date.now()
    while (Date.now() - start < DEFAULT_TIMEOUT) {
      try {
        const detail = await getImprovement(improvementId)
        if (detail.status === 'done') {
          await queryClient.invalidateQueries({ queryKey: ['resumes:detail', resumeId] })
          return { ok: true }
        }
        if (detail.status === 'failed') {
          return { ok: false, error: detail.error || 'Улучшение завершилось с ошибкой' }
        }
      } catch (e: any) {
        return { ok: false, error: 'Ошибка получения статуса улучшения' }
      }
      await new Promise((r) => setTimeout(r, DEFAULT_INTERVAL))
    }
    return { ok: false, error: 'Время ожидания истекло' }
  }

  const onClick = async () => {
    setStatus('running')
    setError(null)
    setMessage('Идёт улучшение…')
    try {
      const res = await enqueueImprove(resumeId)
      const out = await poll(res.improvement_id)
      if (!isMounted.current) return
      if (out.ok) {
        setStatus('idle')
        setMessage(null)
        // refetch resume details explicitly
        await queryClient.fetchQuery({
          queryKey: ['resumes:detail', resumeId],
          queryFn: () => getResume(resumeId),
        })
      } else {
        setStatus('error')
        setError(out.error || 'Ошибка улучшения')
      }
    } catch (e: any) {
      const status = e?.response?.status
      if (status === 409) {
        setError('Улучшение уже выполняется')
      } else if (status === 404) {
        setError('Резюме не найдено')
      } else {
        setError('Не удалось запустить улучшение')
      }
      setStatus('error')
    }
  }

  return (
    <div className="my-3">
      {error && (
        <Alert variant="danger" className="mb-2">
          {error}{' '}
          <Button size="sm" variant="outline-danger" onClick={onClick} className="ms-2">
            Попробовать снова
          </Button>
        </Alert>
      )}
      {status === 'running' && (
        <Alert variant="info" className="mb-2">
          {message || 'Идёт улучшение…'}
        </Alert>
      )}
      <Button onClick={onClick} disabled={status === 'running'}>
        {status === 'running' ? 'Улучшаем…' : 'Улучшить'}
      </Button>
    </div>
  )}
