import pytest
from fastapi.testclient import TestClient

from api.main import app, appointments


client = TestClient(app)



@pytest.fixture(autouse=True)
def clear_appointments():
    appointments.clear()
    yield
    appointments.clear()



def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_empty_appointments():
    response = client.get("/appointments")

    assert response.status_code == 200
    assert response.json() == []


def test_create_appointment():
    appointment_data = {
        "patient_id": 10,
        "doctor_name": "Dr. Ziv Efrati",
        "appointment_time": "2030-09-10T10:30:00Z",
        "reason": "Regular checkup",
    }

    response = client.post(
        "/appointments",
        json=appointment_data,
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["id"] == 1
    assert response_body["patient_id"] == 10
    assert response_body["status"] == "scheduled"


def test_appointment_not_found():
    response = client.get("/appointments/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Appointment not found"
    }


def test_simulated_error():
    response = client.get("/simulate-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Simulated internal server error"
    }


def test_delete_appointment():
    appointment_data = {
        "patient_id": 10,
        "doctor_name": "Dr. Omer Basha",
        "appointment_time": "2026-09-10T10:50:00",
        "reason": "Regular checkup and blood pressure",
    }

    create_response = client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201

    appointment_id = create_response.json()["id"]

    delete_response = client.delete(f"/appointments/{appointment_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Appointment not found"}
