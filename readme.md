# Parking Slot Booking App

A full-stack web application designed for managing and reserving company parking slots efficiently. The application consists of a modern, responsive React frontend and a robust FastAPI backend with built-in validation rules, role-based access control, and an audit-friendly history log suitable for Business Intelligence (e.g., Power BI).

## 🚀 Features

### **Frontend (UI/UX)**
- **Modern Interface**: Built with React 19, Vite, and Framer Motion for smooth animations and transitions.
- **Interactive Booking**: Easy-to-use interface to view available slots grouped by area, and book them for allowed dates.
- **Safe Cancellations**: Allows users to cancel their active bookings securely, complete with a confirmation dialog to prevent accidental clicks.
- **Visual Status**: Clear visual indicators for slot states (Available, Booked, Locked, Restricted).

### **Backend & Business Logic**
- **Robust API**: Powered by FastAPI, offering fast, strongly-typed, and documented REST endpoints.
- **Smart Validation Engine**:
  - **Date Boundaries**: Restricts bookings exclusively to working days (Today & Next Working Day).
  - **Fair Usage**: Limits users to a single active booking per day to prevent hoarding.
  - **Role-based Access**: "Guests" cannot book restricted areas.
  - **User-specific Restrictions**: Only VIP employees can book designated areas (e.g., the 'Kaltezon' zone).
  - **Pre-booked Logic**: Support for permanently assigned slots (e.g., CEO pre-booking logic).
- **Security & Ownership**: Only the original owner of a booking or an administrator can cancel an active reservation.
- **Persistence**: Relational data modeling using SQLAlchemy and SQLite (easily adaptable for PostgreSQL or SQL Server via environment variables).

### **Data & Analytics (Power BI Ready)**
- Features an append-only `parking_booking_history` table that meticulously logs every event (`BOOKED`, `CANCELLED`, `FAILED`, `PREBOOKED`).
- Captures detailed audit trails including timestamps, user identities, actions, results, and rejection reasons to easily monitor usage, generate capacity reports, and connect seamlessly with analytical tools like Power BI.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, Vite, Framer Motion, Lucide React
- **Backend**: Python 3, FastAPI, SQLAlchemy, Uvicorn, SQLite
- **Deployment Ready**: Project structure is configured for straightforward deployment on cloud platforms (like Railway).

---

## 💻 Local Development Setup

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload --port 8000
```
*The backend API will run at `http://localhost:8000`. The SQLite database will be auto-generated at `backend/parking.db`.*

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The Vite application will typically be accessible at `http://localhost:5173`.*

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Simple health check. |
| `GET` | `/api/config` | Returns system configuration, business rules, and allowed employees. |
| `GET` | `/api/slots` | Returns a metadata list of all parking slots. |
| `GET` | `/api/availability` | Returns the categorized availability matrix for a requested date. |
| `POST` | `/api/book` | Submits a new booking. Validates against all business rules before confirming. |
| `POST` | `/api/cancel` | Cancels an active booking (requires ownership/admin). |
| `GET` | `/api/history` | Fetches the comprehensive audit log of system actions. |

---

## 📊 Power BI Integration

For local testing, you can directly connect Power BI Desktop to the `backend/parking.db` file using an **SQLite ODBC driver**.
Useful tables to load:
- `parking_booking_history`: Primary fact table for timeline and audit reporting.
- `parking_bookings`: Current state table (active/cancelled bookings).
- `parking_slots`: Dimension table for slot and area metadata.

*For production deployments, change the `DATABASE_URL` to a robust SQL database (e.g., PostgreSQL, SQL Server) and connect Power BI directly there for real-time reporting.*
