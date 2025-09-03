import asyncio

from tests.conftest import register_and_login


def test_improvement_dedup_enabled(client):
    headers = register_and_login(client, "dedup@example.com")

    # create resume
    r = client.post(
        "/api/v1/resume",
        headers=headers,
        json={"title": "CV", "content": "Original Content"},
    )
    assert r.status_code == 201
    resume_id = r.json()["id"]

    # Pre-create a queued improvement directly in DB to simulate an active task
    async def _create_active_duplicate():
        from app.db.session import AsyncSessionLocal  # noqa: WPS433
        from app.uow import UnitOfWork  # noqa: WPS433

        async with AsyncSessionLocal() as session:
            uow = UnitOfWork(session)
            imp = await uow.improvements.create_queued(
                resume_id=resume_id, old_content="Original Content"
            )
            await uow.commit()
            return str(imp.id)

    asyncio.get_event_loop().run_until_complete(_create_active_duplicate())

    # Now enqueue via API should conflict due to dedup
    r2 = client.post(f"/api/v1/resume/{resume_id}/improve", headers=headers)
    assert r2.status_code == 409
    body = r2.json()
    assert body["error"]["code"] == "duplicate"
