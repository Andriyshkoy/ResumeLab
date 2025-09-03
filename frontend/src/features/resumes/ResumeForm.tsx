import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button, Col, Form, Row } from 'react-bootstrap'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'

const schema = z.object({
  title: z
    .string()
    .max(200, 'Максимум 200 символов')
    .refine((v) => v.trim().length >= 1, { message: 'Введите заголовок' }),
  content: z
    .string()
    .max(50000, 'Максимум 50000 символов')
    .refine((v) => v.trim().length >= 1, { message: 'Введите содержание' }),
})

export type ResumeFormValues = z.infer<typeof schema>

export function ResumeForm({
  initial,
  onSubmit,
  onCancel,
  submitting,
}: {
  initial?: Partial<ResumeFormValues>
  onSubmit: (values: ResumeFormValues) => void | Promise<void>
  onCancel?: () => void
  submitting?: boolean
}) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ResumeFormValues>({ resolver: zodResolver(schema) })

  useEffect(() => {
    if (initial?.title !== undefined) setValue('title', initial.title)
    if (initial?.content !== undefined) setValue('content', initial.content)
  }, [initial, setValue])

  const content = watch('content') || ''
  const title = watch('title') || ''

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <Form.Group className="mb-3">
        <Form.Label>
          Title <small className="text-muted">({title.length}/200)</small>
        </Form.Label>
        <Form.Control type="text" {...register('title')} />
        {errors.title && <Form.Text className="text-danger">{errors.title.message}</Form.Text>}
      </Form.Group>
      <Row>
        <Col md={6} className="mb-3">
          <Form.Label>
            Content <small className="text-muted">({content.length}/50000)</small>
          </Form.Label>
          <Form.Control as="textarea" rows={14} {...register('content')} />
          {errors.content && (
            <Form.Text className="text-danger">{errors.content.message}</Form.Text>
          )}
        </Col>
        <Col md={6} className="mb-3">
          <Form.Label>Предпросмотр</Form.Label>
          <div className="border rounded p-2" style={{ minHeight: 200 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
              {content}
            </ReactMarkdown>
          </div>
        </Col>
      </Row>
      <div className="d-flex gap-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Сохраняем…' : 'Сохранить'}
        </Button>
        {onCancel && (
          <Button variant="secondary" onClick={onCancel} disabled={submitting}>
            Отменить
          </Button>
        )}
      </div>
    </Form>
  )
}
