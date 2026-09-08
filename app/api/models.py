from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"


class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)
    doctor_name: str = Field(min_length=2, max_length=100)
    appointment_time: datetime
    reason: str = Field(min_length=2, max_length=500)


class Appointment(AppointmentCreate):
    id: int
    status: AppointmentStatus = AppointmentStatus.scheduled