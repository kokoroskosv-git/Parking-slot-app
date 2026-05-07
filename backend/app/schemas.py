from datetime import date, datetime
from pydantic import BaseModel

class SlotOut(BaseModel):
    id: int
    slot_code: str
    area_id: str
    area_name: str
    is_restricted: bool
    is_locked: bool

class BookingOut(BaseModel):
    id: int
    booking_date: date
    slot_code: str
    area_id: str
    area_name: str
    person_name: str
    person_type: str
    booking_type: str
    created_at: datetime

class AvailabilitySlot(BaseModel):
    slot_id: int
    slot_code: str
    is_locked: bool
    booking: BookingOut | None = None

class AvailabilityArea(BaseModel):
    area_id: str
    area_name: str
    is_restricted: bool
    allowed_users: list[str]
    slots: list[AvailabilitySlot]

class AvailabilityOut(BaseModel):
    booking_date: date
    allowed_dates: list[date]
    employees: list[str]
    areas: list[AvailabilityArea]

class CreateBookingIn(BaseModel):
    booking_date: date
    slot_code: str
    person_name: str
    person_type: str = "employee"  # employee or guest
    requested_by: str | None = None

class CancelBookingIn(BaseModel):
    booking_id: int
    requested_by: str

class MessageOut(BaseModel):
    message: str
    booking: BookingOut | None = None
