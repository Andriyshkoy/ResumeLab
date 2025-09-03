import { Spinner } from 'react-bootstrap'

export function Loader({ label }: { label?: string }) {
  return (
    <div className="d-flex align-items-center gap-2">
      <Spinner animation="border" size="sm" />
      {label && <span>{label}</span>}
    </div>
  )
}

