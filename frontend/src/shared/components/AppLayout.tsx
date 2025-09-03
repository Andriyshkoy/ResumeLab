import { Container, Nav, Navbar } from 'react-bootstrap'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/auth.store'

export function AppLayout() {
  const navigate = useNavigate()
  const { isAuthed, userEmail, logout } = useAuth()

  const onLogout = () => {
    logout()
    navigate('/auth/login', { replace: true })
  }

  return (
    <>
      <Navbar bg="light" expand="lg" className="mb-3">
        <Container>
          <Navbar.Brand as={Link} to="/resumes">
            ResumeLab
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              {isAuthed && (
                <Nav.Link as={Link} to="/resumes">
                  Мои резюме
                </Nav.Link>
              )}
            </Nav>
            <Nav className="ms-auto align-items-center">
              {isAuthed ? (
                <>
                  <Navbar.Text className="me-3">{userEmail}</Navbar.Text>
                  <Nav.Link onClick={onLogout}>Выйти</Nav.Link>
                </>
              ) : (
                <Nav.Link as={Link} to="/auth/login">
                  Войти
                </Nav.Link>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container>
        <Outlet />
      </Container>
    </>
  )
}

