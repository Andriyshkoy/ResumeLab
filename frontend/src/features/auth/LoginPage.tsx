import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Alert, Button, Card, Form } from 'react-bootstrap'
import { login } from './api'
import { setAuth } from './auth.store'
import { useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'

const schema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Минимум 6 символов').max(128, 'Максимум 128 символов'),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const {
    register: rfRegister,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const onSubmit = async (values: FormValues) => {
    setLoading(true)
    setError(null)
    try {
      const res = await login(values)
      setAuth(res.access_token, res.expires_in, values.email)
      navigate('/resumes', { replace: true })
    } catch (e: any) {
      const msg = e?.response?.status === 401 ? 'Неверный email или пароль' : 'Ошибка входа'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="d-flex justify-content-center">
      <Card style={{ maxWidth: 420, width: '100%' }}>
        <Card.Body>
          <Card.Title>Вход</Card.Title>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit(onSubmit)}>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control type="email" placeholder="you@example.com" {...rfRegister('email')} />
              {errors.email && <Form.Text className="text-danger">{errors.email.message}</Form.Text>}
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Пароль</Form.Label>
              <Form.Control type="password" placeholder="••••••" {...rfRegister('password')} />
              {errors.password && (
                <Form.Text className="text-danger">{errors.password.message}</Form.Text>
              )}
            </Form.Group>
            <div className="d-grid gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? 'Входим…' : 'Войти'}
              </Button>
              <div className="text-center">
                Нет аккаунта? <Link to="/auth/register">Зарегистрироваться</Link>
              </div>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  )
}

