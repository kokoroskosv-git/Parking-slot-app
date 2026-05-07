# Parking Booking App

Internal parking reservation platform built for Evolute.

The application allows employees and guests to reserve parking slots, manage bookings, review booking history, and expose data for reporting tools such as Power BI.

---

# Features

## Booking Management

* Reserve parking slots per day
* Guest and employee booking modes
* One booking per person per day
* Restricted parking areas for specific employees only
* Prebooked/locked slots support
* Remove bookings
* Automatic availability refresh

## Mobile Friendly UI

* Responsive design
* Sticky mobile booking summary bar
* Smooth notifications/toasts
* Mobile home screen icon support (PWA-style)

## Maps & Directions

* Open parking locations directly in Google Maps
* Slot and area directions support

## Reporting & Audit

* Booking history persistence
* `/api/history` endpoint for Power BI integration
* PostgreSQL support for production persistence

## Additional Functionality

* SharePoint PDF rules link
* Remember last selected employee on mobile
* Smooth scrolling navigation
* Railway deployment ready

---

# Tech Stack

## Frontend

* React
* Vite
* CSS
* Lucide React icons

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

## Deployment

* Railway
* GitHub

---

# Project Structure

```text
Parking-slot-app/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── main.py
│
└── README.md
```

---

# Frontend Setup

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Frontend runs by default on:

```text
http://localhost:5173
```

## Frontend Environment Variable

Create `.env` inside `/frontend`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

For production:

```env
VITE_API_BASE_URL=https://YOUR-BACKEND.up.railway.app
```

---

# Backend Setup

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs by default on:

```text
http://localhost:8000
```

## Backend Environment Variables

Create `.env` inside `/backend`:

```env
DATABASE_URL=sqlite:///./parking.db
ALLOWED_ORIGINS=http://localhost:5173
```

For production:

```env
DATABASE_URL=postgresql+psycopg://...
ALLOWED_ORIGINS=https://YOUR-FRONTEND.up.railway.app
```

---

# PostgreSQL Migration

The app originally used SQLite.

For production deployments PostgreSQL is recommended.

## Railway PostgreSQL

1. Add PostgreSQL service in Railway
2. Add backend variable:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

3. Redeploy backend service

---

# Railway Deployment

## Architecture

Recommended Railway setup:

```text
Frontend Service
Backend Service
PostgreSQL Service
```

---

## Frontend Railway Settings

### Root Directory

```text
/frontend
```

### Build Command

```bash
npm install && npm run build
```

### Start Command

```bash
npm run start
```

### Variables

```env
VITE_API_BASE_URL=https://YOUR-BACKEND.up.railway.app
```

---

## Backend Railway Settings

### Root Directory

```text
/backend
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Variables

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=https://YOUR-FRONTEND.up.railway.app
```

---

# API Endpoints

## Health Check

```http
GET /api/health
```

Returns application status.

---

## Availability

```http
GET /api/availability
```

Returns:

* available slots
* bookings
* employees
* areas
* allowed dates

---

## Create Booking

```http
POST /api/book
```

Creates a parking booking.

---

## Remove Booking

```http
DELETE /api/bookings/{booking_id}
```

Removes booking.

---

## Booking History

```http
GET /api/history
```

Power BI friendly booking history endpoint.

---

# Power BI Integration

The backend exposes a reporting endpoint:

```text
https://YOUR-BACKEND.up.railway.app/api/history
```

In Power BI:

```text
Get Data → Web
```

Paste the endpoint URL.

Suggested visuals:

* bookings per day
* occupancy rate
* area utilization
* employee usage
* guest usage
* cancellations
* booking trends

---

# Mobile Shortcut / App Icon

The application supports mobile shortcut icons.

Files:

```text
frontend/public/icon-192.png
frontend/public/manifest.json
```

Recommended icon:

* simplified Evolute “e” logo
* rounded square background
* high contrast

---

# SharePoint Rules PDF

The booking panel supports a direct link to parking rules.

Example:

```js
const RULES_PDF_URL = "https://sharepoint-link.pdf";
```

---

# Security Notes

Current version is intended for internal company usage.

Potential future improvements:

* employee authentication
* admin panel
* booking approvals
* Azure AD / Microsoft login
* role-based access

---

# Future Improvements

Suggested roadmap:

* Admin dashboard
* Booking analytics
* Email notifications
* Outlook integration
* QR-based parking validation
* Automatic booking expiration
* Calendar integration
* Multi-office support

---

# Troubleshooting

## Frontend loads but no data

Check:

```env
VITE_API_BASE_URL
```

Redeploy frontend after changing variables.

---

## CORS Errors

Check backend variable:

```env
ALLOWED_ORIGINS
```

Must exactly match frontend domain.

---

## Railway 404 on `/availability`

Requests must use:

```text
/api/availability
```

not:

```text
/availability
```

---

## PostgreSQL Driver Error

Ensure `requirements.txt` contains:

```text
psycopg[binary]
```

---

# License

Internal Evolute application.

Not intended for public distribution.
