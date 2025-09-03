from tests.conftest import register_and_login


def test_improvement_flow_eager(client):
    headers = register_and_login(client, "imp@example.com")

    # create resume
    r = client.post(
        "/api/v1/resume",
        headers=headers,
        json={"title": "CV", "content": "Original"},
    )
    assert r.status_code == 201
    resume_id = r.json()["id"]

    # enqueue improvement
    r = client.post(f"/api/v1/resume/{resume_id}/improve", headers=headers)
    assert r.status_code == 202
    imp_id = r.json()["improvement_id"]

    # since eager is on, should be done immediately
    r = client.get(f"/api/v1/improvements/{imp_id}", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "done"
    assert data["applied"] is True
    assert data["new_content"].endswith("[Improved]")

    # resume content updated
    r = client.get(f"/api/v1/resume/{resume_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["content"].endswith("[Improved]")
