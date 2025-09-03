import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Alert, Button, Card, Form } from 'react-bootstrap'
import { register as apiRegister } from './api'
import { useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'

const schema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Минимум 6 символов').max(128, 'Максимум 128 символов'),
})

type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const navigate = useNavigate()

  const onSubmit = async (values: FormValues) => {
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      await apiRegister(values)
      setSuccess('Успешная регистрация. Войдите с вашими данными.')
      setTimeout(() => navigate('/auth/login', { replace: true }), 600)
    } catch (e: any) {
      const status = e?.response?.status
      const msg =
        status === 409
          ? 'Email уже занят'
          : status === 422
            ? 'Проверьте введённые данные'
            : 'Ошибка регистрации'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="d-flex justify-content-center">
      <Card style={{ maxWidth: 420, width: '100%' }}>
        <Card.Body>
          <Card.Title>Регистрация</Card.Title>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleSubmit(onSubmit)}>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control type="email" placeholder="you@example.com" {...register('email')} />
              {errors.email && <Form.Text className="text-danger">{errors.email.message}</Form.Text>}
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Пароль</Form.Label>
              <Form.Control type="password" placeholder="••••••" {...register('password')} />
              {errors.password && (
                <Form.Text className="text-danger">{errors.password.message}</Form.Text>
              )}
            </Form.Group>
            <div className="d-grid gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? 'Создаём…' : 'Зарегистрироваться'}
              </Button>
              <div className="text-center">
                Уже есть аккаунт? <Link to="/auth/login">Войти</Link>
              </div>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  )
}

