import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Form, Table } from 'react-bootstrap'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { listResumes, createResume, deleteResume } from './api'
import { useState } from 'react'
import { ResumeForm, type ResumeFormValues } from './ResumeForm'
import { Pagination } from '../../shared/components/Pagination'

const DEFAULT_LIMIT = 20

export function ResumesListPage() {
  const [params, setParams] = useSearchParams()
  const limit = Number(params.get('limit') || DEFAULT_LIMIT)
  const offset = Number(params.get('offset') || 0)
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['resumes:list', { limit, offset }],
    queryFn: () => listResumes({ limit, offset }),
  })

  const onCreate = async (values: ResumeFormValues) => {
    try {
      const created = await createResume({ title: values.title, content: values.content })
      setCreating(false)
      await qc.invalidateQueries({ queryKey: ['resumes:list'] })
      navigate(`/resumes/${created.id}`)
    } catch (e: any) {
      const status = e?.response?.status
      setError(status === 422 ? 'Проверьте поля формы' : 'Не удалось создать резюме')
    }
  }

  const onDelete = async (id: string) => {
    if (!confirm('Удалить резюме?')) return
    await deleteResume(id)
    await qc.invalidateQueries({ queryKey: ['resumes:list'] })
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="mb-0">Мои резюме</h3>
        <div className="d-flex gap-2 align-items-center">
          <Form.Select
            size="sm"
            value={limit}
            onChange={(e) => setParams({ limit: e.target.value, offset: '0' })}
            style={{ width: 100 }}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </Form.Select>
          <Button onClick={() => setCreating(true)}>Создать резюме</Button>
        </div>
      </div>

      {creating && (
        <div className="mb-4">
          <h5>Новое резюме</h5>
          {error && <Alert variant="danger">{error}</Alert>}
          <ResumeForm onSubmit={onCreate} onCancel={() => setCreating(false)} />
        </div>
      )}

      {isLoading && <div>Загрузка…</div>}
      {isError && <Alert variant="danger">Не удалось загрузить список</Alert>}

      {data && (
        <>
          {data.items.length === 0 ? (
            <Alert variant="secondary">Список пуст. Создайте первое резюме.</Alert>
          ) : (
            <Table hover responsive>
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Создано</th>
                  <th>Обновлено</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((r) => (
                  <tr key={r.id}>
                    <td>{r.title}</td>
                    <td>{new Date(r.created_at).toLocaleString()}</td>
                    <td>{new Date(r.updated_at).toLocaleString()}</td>
                    <td className="text-end">
                      <Button as={Link as any} to={`/resumes/${r.id}`} size="sm" className="me-2">
                        Открыть
                      </Button>
                      <Button variant="outline-danger" size="sm" onClick={() => onDelete(r.id)}>
                        Удалить
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
          <Pagination
            total={data.total}
            limit={data.limit}
            offset={data.offset}
            onChange={({ limit, offset }) => setParams({ limit: String(limit), offset: String(offset) })}
          />
        </>
      )}
    </div>
  )
}
