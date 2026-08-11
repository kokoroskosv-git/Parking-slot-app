# Parking Booking Full-Stack App

This version combines the polished React booking UI with a FastAPI backend, persistent SQLite storage, API-driven validation, and an append-only booking history table for Power BI.

## Included features

1. Real availability engine through `/api/availability`.
2. Backend booking validation: allowed dates, one booking per person per day, VIP/Kaltezon restrictions, guest restrictions, slot availability.
3. Persistent bookings in `parking_bookings` using SQLite by default.
4. REST API endpoints: `/api/slots`, `/api/availability`, `/api/book`, `/api/cancel`, `/api/history`.
5. Power BI-friendly history table: `parking_booking_history`.
6. EO-1 is prebooked for AthanasiouL by default, but the prebooking can be released for an individual day without being recreated automatically.

## Run backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The SQLite database will be created at `backend/parking.db`.

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://localhost:5173`.

## Power BI connection

For a quick local test, connect Power BI Desktop to the SQLite file `backend/parking.db` using an SQLite ODBC driver, then load:

- `parking_booking_history` for audit/reporting events
- `parking_bookings` for current/cancelled booking state
- `parking_slots` for slot/area metadata

For production, set `DATABASE_URL` to SQL Server/PostgreSQL instead of SQLite and connect Power BI directly to that database.

## Useful API endpoints

- `GET http://localhost:8000/api/availability`
- `GET http://localhost:8000/api/availability?booking_date=YYYY-MM-DD`
- `POST http://localhost:8000/api/book`
- `POST http://localhost:8000/api/cancel`
- `GET http://localhost:8000/api/history`
