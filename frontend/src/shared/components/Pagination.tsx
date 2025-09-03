import { Pagination as BSPagination } from 'react-bootstrap'

export function Pagination({
  total,
  limit,
  offset,
  onChange,
}: {
  total: number
  limit: number
  offset: number
  onChange: (opts: { limit: number; offset: number }) => void
}) {
  const currentPage = Math.floor(offset / limit) + 1
  const totalPages = Math.max(1, Math.ceil(total / limit))

  const go = (page: number) => {
    const p = Math.min(Math.max(1, page), totalPages)
    onChange({ limit, offset: (p - 1) * limit })
  }

  if (totalPages <= 1) return null
  return (
    <BSPagination className="mt-3">
      <BSPagination.First onClick={() => go(1)} disabled={currentPage === 1} />
      <BSPagination.Prev onClick={() => go(currentPage - 1)} disabled={currentPage === 1} />
      <BSPagination.Item active>{currentPage}</BSPagination.Item>
      <BSPagination.Next onClick={() => go(currentPage + 1)} disabled={currentPage >= totalPages} />
      <BSPagination.Last onClick={() => go(totalPages)} disabled={currentPage >= totalPages} />
    </BSPagination>
  )
}

