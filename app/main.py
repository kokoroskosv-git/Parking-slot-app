from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import ParkingEntry

app = FastAPI()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="app/templates")

# -------------------------
# Users & Locations
# -------------------------
USERS = [
    "Athanasiou", "Korogiannakis", "Kokoroskos", "Petris",
    "Tzedakis", "Lampos", "Koumentis", "Nikolaidis",
    "Fostiropoulou", "Guest1", "Guest2"
]

LOCATIONS = {
    "Office": 2,
    "Amarousiou-Chalandriou": 2,
    "Kaltezon": 2
}

GROUP_1 = {"Kokoroskos", "Nikolaidis", "Fostiropoulou", "Tzedakis","Guest1", "Guest2"}
GROUP_1_ALLOWED_LOCATIONS = {"Office", "Amarousiou-Chalandriou"}

CEO_NAME = "Athanasiou"
CEO_LOCATION = "Office"
CEO_PREBOOK_UNTIL = date(2026, 12, 31)

# -------------------------
# Date helpers
# -------------------------
def is_working_day(d: date) -> bool:
    return d.weekday() < 5

def get_next_working_day(d: date) -> date:
    d += timedelta(days=1)
    while not is_working_day(d):
        d += timedelta(days=1)
    return d

def get_standard_booking_days():
    today = date.today()
    if not is_working_day(today):
        today = get_next_working_day(today)
    return [today, get_next_working_day(today)]

# -------------------------
# CEO Prebooking
# -------------------------
def create_ceo_prebook_if_missing(db: Session, day: date):
    if not is_working_day(day) or day > CEO_PREBOOK_UNTIL:
        return

    existing = db.query(ParkingEntry).filter(
        ParkingEntry.entry_date == day,
        ParkingEntry.user_name == CEO_NAME
    ).first()

    # Αν έχει ακυρωθεί επίτηδες, μην τον ξαναδημιουργήσεις
    if existing and existing.entry_type == "ceo_cancelled":
        return

    if not existing:
        db.add(ParkingEntry(
            user_name=CEO_NAME,
            entry_date=day,
            entry_type="prebook",
            location=CEO_LOCATION
        ))

# -------------------------
# Home
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, message: str | None = None):
    calendar_days = get_standard_booking_days()

    with SessionLocal() as db:

        # Δημιουργία CEO prebook μόνο όπου χρειάζεται
        for day in calendar_days:
            create_ceo_prebook_if_missing(db, day)
        db.commit()

        remaining_by_location = {}
        calendar_data = {}

        for day in calendar_days:
            calendar_data[day] = {}
            for loc, max_places in LOCATIONS.items():
                bookings = db.query(ParkingEntry).filter(
                    ParkingEntry.entry_date == day,
                    ParkingEntry.location == loc,
                    ParkingEntry.entry_type != "ceo_cancelled"
                ).all()

                calendar_data[day][loc] = {"bookings": bookings}
                remaining_by_location.setdefault(loc, {})[day] = max(
                    max_places - len(bookings), 0
                )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "users": USERS,
            "locations": LOCATIONS.keys(),
            "calendar_days": calendar_days,
            "calendar_data": calendar_data,
            "remaining_by_location": remaining_by_location,
            "message": message
        }
    )

# -------------------------
# Create booking
# -------------------------
@app.post("/book")
def book(
    user_name: str = Form(...),
    location: str = Form(...),
    booking_date: str = Form(...)
):
    booking_dt = datetime.strptime(booking_date, "%Y-%m-%d").date()

    if booking_dt not in get_standard_booking_days():
        return RedirectResponse(
            "/?message=Κράτηση επιτρέπεται μόνο για σήμερα ή επόμενη εργάσιμη",
            status_code=303
        )

    if user_name in GROUP_1 and location not in GROUP_1_ALLOWED_LOCATIONS:
        return RedirectResponse(
            "/?message=Δεν έχετε δικαίωμα κράτησης σε αυτό το location",
            status_code=303
        )

    with SessionLocal() as db:
        existing = db.query(ParkingEntry).filter(
            ParkingEntry.entry_date == booking_dt,
            ParkingEntry.user_name == user_name
        ).first()

        # Manual booking για CEO μετά από ακύρωση
        if existing and existing.entry_type == "ceo_cancelled":
            existing.entry_type = "booking"
            existing.location = location
            db.commit()
            return RedirectResponse(
                "/?message=Η κράτηση καταχωρήθηκε",
                status_code=303
            )

        if existing:
            return RedirectResponse(
                f"/?message=Έχετε ήδη κράτηση για {booking_dt.strftime('%d/%m/%Y')}",
                status_code=303
            )

        used = db.query(ParkingEntry).filter(
            ParkingEntry.entry_date == booking_dt,
            ParkingEntry.location == location
        ).count()

        if used >= LOCATIONS[location]:
            return RedirectResponse(
                f"/?message=Δεν υπάρχει διαθεσιμότητα για {location}",
                status_code=303
            )

        db.add(ParkingEntry(
            user_name=user_name,
            entry_date=booking_dt,
            entry_type="booking",
            location=location
        ))
        db.commit()

    return RedirectResponse(
        "/?message=Η κράτηση καταχωρήθηκε",
        status_code=303
    )

# -------------------------
# Cancel booking / prebooking
# -------------------------
@app.post("/cancel")
def cancel_booking(booking_id: int = Form(...)):
    with SessionLocal() as db:
        booking = db.query(ParkingEntry).filter(
            ParkingEntry.id == booking_id
        ).first()

        if booking:
            if booking.user_name == CEO_NAME:
                booking.entry_type = "ceo_cancelled"
            else:
                db.delete(booking)

            db.commit()

    return RedirectResponse(
        "/?message=Η κράτηση ακυρώθηκε",
        status_code=303
    )

