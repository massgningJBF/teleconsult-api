def test_register_and_login(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "a@a.com", "password": "secret123", "role": "patient", "name": "Alice"},
    )
    assert resp.status_code == 201

    resp = client.post("/api/v1/auth/login", json={"email": "a@a.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "a@a.com", "password": "secret123", "role": "patient", "name": "Alice"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": "a@a.com", "password": "wrong"})
    assert resp.status_code == 401


def test_register_duplicate_email(client):
    payload = {"email": "a@a.com", "password": "secret123", "role": "patient", "name": "Alice"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
