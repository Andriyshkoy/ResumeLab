import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Alert, Button } from 'react-bootstrap'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { deleteResume, getResume, updateResume } from './api'
import { ResumeForm, type ResumeFormValues } from './ResumeForm'
import { ImproveButton } from '../improvements/ImproveButton'

export function ResumeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const resumeId = id as string
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['resumes:detail', resumeId],
    queryFn: () => getResume(resumeId),
  })

  const onSave = async (values: ResumeFormValues) => {
    if (!resumeId) return
    await updateResume(resumeId, { title: values.title, content: values.content })
    await qc.invalidateQueries({ queryKey: ['resumes:detail', resumeId] })
  }

  const onDelete = async () => {
    if (!resumeId) return
    if (!confirm('Удалить резюме?')) return
    await deleteResume(resumeId)
    navigate('/resumes', { replace: true })
  }

  if (isLoading) return <div>Загрузка…</div>
  if (isError || !data) return <Alert variant="danger">Не удалось загрузить резюме</Alert>

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-2">
        <h3 className="mb-0">Редактирование резюме</h3>
        <div>
          <Button as={Link as any} to="/resumes" variant="secondary" className="me-2">
            К списку
          </Button>
          <Button variant="outline-danger" onClick={onDelete}>
            Удалить
          </Button>
        </div>
      </div>
      <ImproveButton resumeId={resumeId} />
      <ResumeForm initial={{ title: data.title, content: data.content }} onSubmit={onSave} />
    </div>
  )
}
