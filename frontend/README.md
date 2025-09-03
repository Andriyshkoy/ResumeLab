ResumeLab SPA (Frontend)

Quick start
- Copy `.env.example` to `.env.local` and adjust `VITE_API_BASE_URL` (e.g., http://localhost:8000).
- Install deps: `npm i`
- Run dev: `npm run dev`
- Build: `npm run build` (Node.js 20+ recommended for Vite 7)

ENV
- `VITE_API_BASE_URL`: API base, backend exposes `/api/v1/*`.
- `VITE_AUTH_STORAGE`: `local` (default) or `session` for token store.
- `VITE_POLL_INTERVAL_MS`: default 1000.
- `VITE_POLL_TIMEOUT_MS`: default 60000.

Routes
- `/auth/login`, `/auth/register`
- `/resumes`, `/resumes/:id`

Notes
- JWT is stored in selected storage; 401 responses clear session and redirect to `/auth/login`.
- Axios adds `Authorization` and `X-Request-ID` to protected requests.
- Improvement flow: POST enqueue → 1s polling (timeout 60s) → refresh resume on `done`.

