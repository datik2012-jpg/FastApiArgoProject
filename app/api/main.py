from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .db_models import AppointmentRecord, OutboxEvent
from .logging_config import configure_logging
from .models import Appointment, AppointmentCreate

settings = get_settings()

logger = configure_logging()
logger.info("application_started")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.middleware("http")
async def log_http_request(request: Request, call_next):
    start_time = perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (perf_counter() - start_time) * 1000,
        2,
    )

    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "environment": settings.environment,
        },
    )

    return response


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def readiness():
    return {
        "status": "ready",
        "environment": settings.environment,
    }


@app.get(
    "/appointments/{appointment_id}",
    response_model=Appointment,
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.get(AppointmentRecord, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


@app.post(
    "/appointments",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
):
    with db.begin():
        appointment = AppointmentRecord(**data.model_dump())
        db.add(appointment)
        db.flush()

        response = Appointment.model_validate(appointment)

        event = OutboxEvent(
            appointment_id=appointment.id,
            event_type="appointment.created",
            payload=response.model_dump(mode="json"),
        )
        db.add(event)

    logger.info(
        "appointment_created",
        extra={
            "appointment_id": response.id,
            "environment": settings.environment,
        },
    )

    return response

@app.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
) -> None:
    with db.begin():
        appointment = db.get(
            AppointmentRecord,
            appointment_id,
            with_for_update=True,
        )

        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )

        payload = Appointment.model_validate(
            appointment
        ).model_dump(mode="json")

        db.add(
            OutboxEvent(
                appointment_id=appointment.id,
                event_type="appointment.deleted",
                payload=payload,
            )
        )

        db.delete(appointment)


@app.get("/appointments", response_model=list[Appointment])
def get_appointments(db: Session = Depends(get_db)):
    statement = select(AppointmentRecord).order_by(AppointmentRecord.id)
    return db.scalars(statement).all()


@app.get("/simulate-error")
def simulate_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Simulated internal server error",
    )
