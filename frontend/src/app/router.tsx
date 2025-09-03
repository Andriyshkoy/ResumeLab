import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '../shared/components/AppLayout'
import { LoginPage } from '../features/auth/LoginPage'
import { RegisterPage } from '../features/auth/RegisterPage'
import { ResumesListPage } from '../features/resumes/ResumesListPage'
import { ResumeDetailPage } from '../features/resumes/ResumeDetailPage'
import { RequireAuth } from '../shared/hooks/RequireAuth'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/resumes" replace /> },
      {
        path: 'resumes',
        element: (
          <RequireAuth>
            <ResumesListPage />
          </RequireAuth>
        ),
      },
      {
        path: 'resumes/:id',
        element: (
          <RequireAuth>
            <ResumeDetailPage />
          </RequireAuth>
        ),
      },
    ],
  },
  {
    path: '/auth',
    element: <AppLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/resumes" replace /> },
])

