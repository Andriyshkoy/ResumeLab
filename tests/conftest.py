import os
import tempfile

import pytest


@pytest.fixture(scope="session", autouse=True)
def test_env():
    # Use sqlite file DB for predictable lifecycle
    db_fd, db_path = tempfile.mkstemp(prefix="test_resumelab", suffix=".db")
    os.close(db_fd)
    os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    os.environ.setdefault("JWT_SECRET", "test_secret")
    os.environ.setdefault("ACCESS_TOKEN_TTL", "3600")
    os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")
    os.environ.setdefault("SYNC_DATABASE_URL", f"sqlite:///{db_path}")
    yield
    try:
        os.remove(db_path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def app_instance(test_env):
    # Import after env is set
    import asyncio

    from app.db.base import Base  # noqa: WPS433
    from app.db.session import engine  # noqa: WPS433
    from app.main import app  # noqa: WPS433

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(init_models())
    return app


@pytest.fixture()
def client(app_instance):
    from fastapi.testclient import TestClient  # noqa: WPS433

    with TestClient(app_instance) as c:
        yield c


def register_and_login(client, email: str, password: str = "Passw0rd!"):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert r.status_code in (201, 409)
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
