from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slot_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    area_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    area_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    bookings: Mapped[list["ParkingBooking"]] = relationship(back_populates="slot")

class ParkingBooking(Base):
    __tablename__ = "parking_bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("parking_slots.id"), nullable=False, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    person_type: Mapped[str] = mapped_column(String(20), nullable=False)  # employee, guest, system
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, cancelled
    booking_type: Mapped[str] = mapped_column(String(20), default="booking", nullable=False)  # booking, prebook
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    slot: Mapped[ParkingSlot] = relationship(back_populates="bookings")

class ParkingBookingHistory(Base):
    """Append-only table intended for BI/Power BI reporting."""
    __tablename__ = "parking_booking_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)  # BOOKED, CANCELLED, PREBOOKED, FAILED
    booking_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    booking_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    slot_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    area_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    person_name: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    person_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # SUCCESS, REJECTED
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
