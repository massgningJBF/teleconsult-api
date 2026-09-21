import pytest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _register_and_login(client, email, password, role, name, specialty=None):
    payload = {"email": email, "password": password, "role": role, "name": name}
    if specialty:
        payload["specialty"] = specialty
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def doctor_headers(client):
    return _register_and_login(
        client, "doc@example.com", "secret123", "doctor", "Dr House", specialty="Diagnostic"
    )


@pytest.fixture
def patient_headers(client):
    return _register_and_login(client, "pat@example.com", "secret123", "patient", "Alice")


@pytest.fixture
def booked_slot(client, doctor_headers):
    start = (datetime.utcnow() + timedelta(days=3)).replace(microsecond=0)
    end = start + timedelta(minutes=30)
    resp = client.post(
        "/api/v1/slots/",
        json={"start_time": start.isoformat(), "end_time": end.isoformat()},
        headers=doctor_headers,
    )
    return resp.get_json()
