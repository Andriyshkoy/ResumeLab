import { Alert } from 'react-bootstrap'

export function ErrorBanner({ message }: { message: string }) {
  return (
    <Alert variant="danger" className="my-3">
      {message}
    </Alert>
  )
}

