from fastapi import FastAPI, HTTPException, status

from .config import get_settings
from .models import Appointment, AppointmentCreate


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


appointments: list[Appointment] = []


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def readiness():
    return {
        "status": "ready",
        "environment": settings.environment,
    }


@app.get("/appointments")
def get_appointments() -> list[Appointment]:
    return appointments


@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: int) -> Appointment:
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Appointment not found",
    )


@app.post(
    "/appointments",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(data: AppointmentCreate):
    appointment = Appointment(
        id=max((appointment.id for appointment in appointments), default=0) + 1,
        **data.model_dump(),
    )

    appointments.append(appointment)
    return appointment


@app.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(appointment_id: int) -> None:
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Appointment not found",
    )
