from tests.conftest import register_and_login


def test_resume_crud_and_isolation(client):
    # user A
    headers_a = register_and_login(client, "a@example.com")

    # create
    r = client.post(
        "/api/v1/resume",
        headers=headers_a,
        json={"title": "Python Backend", "content": "Опыт: FastAPI, Postgres..."},
    )
    assert r.status_code == 201
    resume = r.json()
    resume_id = resume["id"]

    # list
    r = client.get("/api/v1/resume", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["total"] == 1

    # get
    r = client.get(f"/api/v1/resume/{resume_id}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["content"].startswith("Опыт")

    # update
    r = client.put(
        f"/api/v1/resume/{resume_id}",
        headers=headers_a,
        json={"title": "Python Dev", "content": "Новый контент"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Python Dev"

    # user B
    headers_b = register_and_login(client, "b@example.com")

    # cannot access A's resume
    r = client.get(f"/api/v1/resume/{resume_id}", headers=headers_b)
    assert r.status_code == 404

    # delete by A
    r = client.delete(f"/api/v1/resume/{resume_id}", headers=headers_a)
    assert r.status_code == 204

    # now 404
    r = client.get(f"/api/v1/resume/{resume_id}", headers=headers_a)
    assert r.status_code == 404
