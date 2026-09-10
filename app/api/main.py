from .config import get_settings
from .models import Appointment, AppointmentCreate

from time import perf_counter
from fastapi import FastAPI, HTTPException, Request, status
from .logging_config import configure_logging

#import debuggy when you want to debug the system + adde debugpy breakpoint in the code

settings = get_settings()

logger = configure_logging()
logger.info("application_started")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


appointments: list[Appointment] = []



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
    #debugpy.breakpoint()  # Temporary forced debugger pause.
    appointment = Appointment(
        id=max((appointment.id for appointment in appointments), default=0) + 1,
        **data.model_dump(),
    )

    appointments.append(appointment)


    logger.info(
        "appointment_created",
        extra={
            "appointment_id": appointment.id,
            "environment": settings.environment,
        },
    )

    return appointment



@app.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(appointment_id: int) -> None:
    #debugpy.breakpoint()
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Appointment not found",
    )

@app.get("/simulate-error")
def simulate_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Simulated internal server error",
    )
