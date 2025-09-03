def test_register_and_login_success(client):
    email = "user1@example.com"
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "S3curePass!"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == email
    assert "id" in data

    r2 = client.post("/api/v1/auth/login", json={"email": email, "password": "S3curePass!"})
    assert r2.status_code == 200
    j = r2.json()
    assert "access_token" in j and j["token_type"] == "bearer"


def test_register_conflict(client):
    email = "dup@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": "S3curePass!"})
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "S3curePass!"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "conflict"


def test_login_invalid_credentials(client):
    r = client.post("/api/v1/auth/login", json={"email": "nouser@example.com", "password": "x"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthorized"
