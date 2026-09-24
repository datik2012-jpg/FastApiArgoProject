from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class AppointmentRecord(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    appointment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="scheduled",
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    event_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    appointment_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )