ResumeLab Backend (FastAPI + Celery)

Quickstart (local without Docker)
- Create venv and install: `pip install -r requirements.txt`
- Run DB migrations (SQLite default): `alembic upgrade head`
- Start API: `uvicorn app.main:app --reload`

Docker Compose
- `docker compose up --build`
- API: http://localhost:8000/docs
- Flower: http://localhost:5555

Testing
- `pytest -q`

Environment
- `DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app`
- `SYNC_DATABASE_URL=postgresql+psycopg://app:app@db:5432/app` (for Alembic)
- `JWT_SECRET=change_me`
- `ACCESS_TOKEN_TTL=3600`
- `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//`
- `LOG_LEVEL=INFO`
