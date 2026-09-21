from datetime import datetime, timedelta


def test_only_doctor_can_create_slot(client, patient_headers):
    start = (datetime.utcnow() + timedelta(days=1)).isoformat()
    end = (datetime.utcnow() + timedelta(days=1, minutes=30)).isoformat()
    resp = client.post(
        "/api/v1/slots/", json={"start_time": start, "end_time": end}, headers=patient_headers
    )
    assert resp.status_code == 403


def test_invalid_slot_duration_rejected(client, doctor_headers):
    start = (datetime.utcnow() + timedelta(days=1)).isoformat()
    end = (datetime.utcnow() + timedelta(days=1, minutes=5)).isoformat()  # 5 min, trop court
    resp = client.post(
        "/api/v1/slots/", json={"start_time": start, "end_time": end}, headers=doctor_headers
    )
    assert resp.status_code == 422


def test_patient_can_book_slot(client, patient_headers, booked_slot):
    resp = client.post(
        "/api/v1/appointments/", json={"slot_id": booked_slot["id"]}, headers=patient_headers
    )
    assert resp.status_code == 201


def test_cannot_double_book_slot(client, patient_headers, booked_slot):
    client.post("/api/v1/appointments/", json={"slot_id": booked_slot["id"]}, headers=patient_headers)
    resp = client.post(
        "/api/v1/appointments/", json={"slot_id": booked_slot["id"]}, headers=patient_headers
    )
    assert resp.status_code == 409


def test_patient_only_sees_own_appointments(client, patient_headers, booked_slot):
    client.post("/api/v1/appointments/", json={"slot_id": booked_slot["id"]}, headers=patient_headers)
    resp = client.get("/api/v1/appointments/", headers=patient_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()["items"]) == 1


def test_booking_without_token_returns_401(client, booked_slot):
    resp = client.post("/api/v1/appointments/", json={"slot_id": booked_slot["id"]})
    assert resp.status_code == 401
