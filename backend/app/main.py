from datetime import date, datetime, timedelta
import os
# pyrefly: ignore [missing-import]
from fastapi import Depends, FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import ParkingBooking, ParkingBookingHistory, ParkingSlot
from .schemas import AvailabilityArea, AvailabilityOut, AvailabilitySlot, BookingOut, CancelBookingIn, CreateBookingIn, MessageOut, SlotOut

app = FastAPI(title="Parking Booking API", version="1.0.0")

allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
)
allowed_origins = [origin.strip().rstrip("/") for origin in allowed_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMPLOYEES = [
    "AthanasiouL", "KorogiannakisN", "NikolaidisK", "PetrisD", "KoumentisN",
    "KokoroskosV", "LamposP", "TzedakisP", "FostiropoulouL", "NikolaidisN",
]
CEO_NAME = "AthanasiouL"
CEO_PREBOOK_UNTIL = date(2026, 12, 31)
VIP_ALLOWED = {"KorogiannakisN", "KoumentisN", "LamposP", "PetrisD"}
AREA_ALLOWED_USERS = {
    "kaltezon": sorted(VIP_ALLOWED),
}
SLOT_SEED = [
    ("EO-1", "evolute-office", "Evolute's Office", False, False, 10),
    ("EO-2", "evolute-office", "Evolute's Office", False, False, 20),
    ("KA-1", "kaltezon", "Kaltezon", True, False, 30),
    ("KA-2", "kaltezon", "Kaltezon", True, False, 40),
    ("AC-1", "amarousiou-chalandriou", "Amarousiou-Chalandriou", False, False, 50),
    ("AC-2", "amarousiou-chalandriou", "Amarousiou-Chalandriou", False, False, 60),
]


def is_working_day(d: date) -> bool:
    return d.weekday() < 5


def next_working_day(d: date) -> date:
    d = d + timedelta(days=1)
    while not is_working_day(d):
        d = d + timedelta(days=1)
    return d


def allowed_booking_dates() -> list[date]:
    today = date.today()
    if not is_working_day(today):
        today = next_working_day(today)
    return [today, next_working_day(today)]


def booking_to_out(booking: ParkingBooking) -> BookingOut:
    return BookingOut(
        id=booking.id,
        booking_date=booking.booking_date,
        slot_code=booking.slot.slot_code,
        area_id=booking.slot.area_id,
        area_name=booking.slot.area_name,
        person_name=booking.person_name,
        person_type=booking.person_type,
        booking_type=booking.booking_type,
        created_at=booking.created_at,
    )


def add_history(
    db: Session,
    *,
    event_type: str,
    result: str,
    reason: str | None = None,
    booking: ParkingBooking | None = None,
    slot: ParkingSlot | None = None,
    booking_date: date | None = None,
    person_name: str | None = None,
    person_type: str | None = None,
    requested_by: str | None = None,
):
    effective_slot = slot or (booking.slot if booking else None)
    db.add(ParkingBookingHistory(
        event_type=event_type,
        booking_id=booking.id if booking else None,
        booking_date=booking.booking_date if booking else booking_date,
        slot_code=effective_slot.slot_code if effective_slot else None,
        area_id=effective_slot.area_id if effective_slot else None,
        area_name=effective_slot.area_name if effective_slot else None,
        person_name=booking.person_name if booking else person_name,
        person_type=booking.person_type if booking else person_type,
        requested_by=requested_by,
        result=result,
        reason=reason,
    ))


def seed_slots(db: Session):
    for slot_code, area_id, area_name, restricted, locked, sort_order in SLOT_SEED:
        existing = db.scalar(select(ParkingSlot).where(ParkingSlot.slot_code == slot_code))
        if not existing:
            db.add(ParkingSlot(
                slot_code=slot_code,
                area_id=area_id,
                area_name=area_name,
                is_restricted=restricted,
                is_locked=locked,
                sort_order=sort_order,
            ))
    db.commit()


def ensure_ceo_prebooks(db: Session):
    for booking_day in allowed_booking_dates():
        if booking_day > CEO_PREBOOK_UNTIL:
            continue
        slot = db.scalar(select(ParkingSlot).where(ParkingSlot.slot_code == "EO-1"))
        if not slot:
            continue
        exists = db.scalar(select(ParkingBooking).where(
            ParkingBooking.booking_date == booking_day,
            ParkingBooking.person_name == CEO_NAME,
            ParkingBooking.status == "active",
        ))
        slot_taken = db.scalar(select(ParkingBooking).where(
            ParkingBooking.booking_date == booking_day,
            ParkingBooking.slot_id == slot.id,
            ParkingBooking.status == "active",
        ))
        if not exists and not slot_taken:
            booking = ParkingBooking(
                booking_date=booking_day,
                slot_id=slot.id,
                person_name=CEO_NAME,
                person_type="employee",
                booking_type="prebook",
                status="active",
            )
            db.add(booking)
            db.flush()
            add_history(db, event_type="PREBOOKED", result="SUCCESS", booking=booking, requested_by="system")
    db.commit()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_slots(db)
        ensure_ceo_prebooks(db)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def config():
    return {
        "employees": EMPLOYEES,
        "allowed_dates": allowed_booking_dates(),
        "area_allowed_users": AREA_ALLOWED_USERS,
        "rules": [
            "Booking is allowed only for today or the next working day.",
            "A person can have only one active booking per day.",
            "Guests cannot book Kaltezon.",
            "Only VIP employees can book Kaltezon.",
            "AthanasiouL is pre-booked in EO-1 until 2026-12-31.",
        ],
    }


@app.get("/api/slots", response_model=list[SlotOut])
def get_slots(db: Session = Depends(get_db)):
    seed_slots(db)
    slots = db.scalars(select(ParkingSlot).order_by(ParkingSlot.sort_order)).all()
    return slots


@app.get("/api/availability", response_model=AvailabilityOut)
def get_availability(booking_date: date | None = None, db: Session = Depends(get_db)):
    seed_slots(db)
    ensure_ceo_prebooks(db)
    dates = allowed_booking_dates()
    target_date = booking_date or dates[0]
    if target_date not in dates:
        raise HTTPException(status_code=400, detail="Booking is allowed only for today or the next working day.")

    slots = db.scalars(select(ParkingSlot).order_by(ParkingSlot.sort_order)).all()
    active_bookings = db.scalars(select(ParkingBooking).where(
        ParkingBooking.booking_date == target_date,
        ParkingBooking.status == "active",
    )).all()
    bookings_by_slot = {b.slot_id: b for b in active_bookings}

    area_map: dict[str, AvailabilityArea] = {}
    for slot in slots:
        if slot.area_id not in area_map:
            area_map[slot.area_id] = AvailabilityArea(
                area_id=slot.area_id,
                area_name=slot.area_name,
                is_restricted=slot.is_restricted,
                allowed_users=AREA_ALLOWED_USERS.get(slot.area_id, []),
                slots=[],
            )
        booking = bookings_by_slot.get(slot.id)
        area_map[slot.area_id].slots.append(AvailabilitySlot(
            slot_id=slot.id,
            slot_code=slot.slot_code,
            is_locked=slot.is_locked,
            booking=booking_to_out(booking) if booking else None,
        ))

    return AvailabilityOut(
        booking_date=target_date,
        allowed_dates=dates,
        employees=EMPLOYEES,
        areas=list(area_map.values()),
    )


@app.post("/api/book", response_model=MessageOut)
def create_booking(payload: CreateBookingIn, db: Session = Depends(get_db)):
    seed_slots(db)
    ensure_ceo_prebooks(db)
    requested_by = payload.requested_by or payload.person_name
    person_name = payload.person_name.strip()
    person_type = payload.person_type.lower().strip()

    slot = db.scalar(select(ParkingSlot).where(ParkingSlot.slot_code == payload.slot_code))
    if not slot:
        add_history(db, event_type="FAILED", result="REJECTED", reason="Slot does not exist", booking_date=payload.booking_date, person_name=person_name, person_type=person_type, requested_by=requested_by)
        db.commit()
        raise HTTPException(status_code=404, detail="Slot does not exist.")

    def reject(message: str, status_code: int = 400):
        add_history(db, event_type="FAILED", result="REJECTED", reason=message, slot=slot, booking_date=payload.booking_date, person_name=person_name, person_type=person_type, requested_by=requested_by)
        db.commit()
        raise HTTPException(status_code=status_code, detail=message)

    if payload.booking_date not in allowed_booking_dates():
        reject("Booking is allowed only for today or the next working day.")
    if not person_name:
        reject("Person name is required.")
    if person_type not in {"employee", "guest"}:
        reject("person_type must be employee or guest.")
    if person_type == "employee" and person_name not in EMPLOYEES:
        reject("Unknown employee.")
    if slot.is_locked:
        reject("This slot is locked.")
    if slot.is_restricted and person_type == "guest":
        reject("Guests cannot book Kaltezon.")
    if slot.is_restricted and person_type == "employee" and person_name not in AREA_ALLOWED_USERS.get(slot.area_id, []):
        reject("Selected employee is not allowed in Kaltezon.")

    existing_person_booking = db.scalar(select(ParkingBooking).where(
        ParkingBooking.booking_date == payload.booking_date,
        ParkingBooking.person_name == person_name,
        ParkingBooking.status == "active",
    ))
    if existing_person_booking:
        reject("This person already has one active booking for the selected day.", 409)

    existing_slot_booking = db.scalar(select(ParkingBooking).where(
        ParkingBooking.booking_date == payload.booking_date,
        ParkingBooking.slot_id == slot.id,
        ParkingBooking.status == "active",
    ))
    if existing_slot_booking:
        reject("This slot is no longer available.", 409)

    booking = ParkingBooking(
        booking_date=payload.booking_date,
        slot_id=slot.id,
        person_name=person_name,
        person_type=person_type,
        booking_type="booking",
        status="active",
    )
    db.add(booking)
    db.flush()
    add_history(db, event_type="BOOKED", result="SUCCESS", booking=booking, requested_by=requested_by)
    db.commit()
    db.refresh(booking)
    return MessageOut(message="The booking is successfully made.", booking=booking_to_out(booking))


@app.post("/api/cancel", response_model=MessageOut)
def cancel_booking(payload: CancelBookingIn, db: Session = Depends(get_db)):
    booking = db.scalar(select(ParkingBooking).where(ParkingBooking.id == payload.booking_id))
    if not booking or booking.status != "active":
        add_history(db, event_type="FAILED", result="REJECTED", reason="Active booking was not found", requested_by=payload.requested_by)
        db.commit()
        raise HTTPException(status_code=404, detail="Active booking was not found.")

    is_guest_booking = booking.person_type == "guest"
    is_owner = payload.requested_by == booking.person_name
    is_admin = payload.requested_by == "admin"

    if not (is_guest_booking or is_owner or is_admin):
        add_history(
            db,
            event_type="FAILED",
            result="REJECTED",
            reason="Only the booking owner or admin can cancel this booking",
            booking=booking,
            requested_by=payload.requested_by,
        )
        db.commit()
        raise HTTPException(status_code=403, detail="Only the booking owner or admin can cancel this booking.")

    booking.status = "cancelled"
    booking.cancelled_at = datetime.utcnow()
    booking.cancelled_by = payload.requested_by
    add_history(db, event_type="CANCELLED", result="SUCCESS", booking=booking, requested_by=payload.requested_by)
    db.commit()
    return MessageOut(message="The booking was cancelled.", booking=None)



@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ParkingBookingHistory)
        .order_by(ParkingBookingHistory.event_ts.desc())
    ).all()

    return [
        {
            "history_id": row.id,
            "event_ts": row.event_ts,
            "event_type": row.event_type,
            "result": row.result,
            "reason": row.reason,
            "booking_id": row.booking_id,
            "booking_date": row.booking_date,
            "slot_code": row.slot_code,
            "area_id": row.area_id,
            "area_name": row.area_name,
            "person_name": row.person_name,
            "person_type": row.person_type,
            "requested_by": row.requested_by,
        }
        for row in rows
    ]