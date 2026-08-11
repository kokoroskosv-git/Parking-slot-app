import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  CalendarClock,
  CheckCircle2,
  CircleParking,
  Mail,
  MapPin,
  RefreshCw,
  Trash2,
  UserPlus,
  Users,
  X,
  XCircle,
} from "lucide-react";
import EvoluteLogo from "./EvoluteLogo.jsx";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const RULES_PDF_URL = "https://bpmsa.sharepoint.com/:b:/s/evolute_hub/IQDB46UaHiO5S4nzwKAtBZxfAQLf87F2ZMHbm6fG8fx0H24?e=4oWWLp";
const AREA_INFO = {
  "evolute-office": {
    directions: "Use the Evolute office parking entrance and park only in the assigned EO slot.",
    mapUrl: "https://maps.google.com/?q=Evolute%20Athens",
  },
  kaltezon: {
    directions: "Restricted parking area. Use only if you are one of the allowed employees and park in the assigned KA slot.",
    mapUrl: "https://maps.app.goo.gl/FrMgh3seE1vBC4LN9",
  },
  "amarousiou-chalandriou": {
    directions: "Use the Amarousiou-Chalandriou parking entrance and park only in the assigned AC slot.",
    mapUrl: "https://maps.app.goo.gl/ECoFioUCfCzmqLhe7",
  },
};

function formatDateLabel(value) {
  if (!value) return "";
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed");
  }

  return data;
}

function buildDirectionsEmail({ guestName, areaName, slotCode, bookingDate, mapUrl, directions }) {
  const subject = "Parking directions for your visit";
  const body = [
    `Hello ${guestName},`,
    "",
    "Here are the parking directions for your visit.",
    "",
    `Parking area: ${areaName}`,
    `Parking slot: ${slotCode}`,
    `Booking date: ${formatDateLabel(bookingDate)}`,
    "",
    "Directions:",
    directions || "Please follow the assigned parking instructions.",
    "",
    "Map:",
    mapUrl || "Map link not available",
    "",
    "Please use the assigned slot upon arrival.",
  ].join("\n");

  return `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

function GuestDirectionsDialog({ prompt, onClose }) {
  if (!prompt) return null;

  const mailtoUrl = buildDirectionsEmail(prompt);

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <X size={18} />
        </button>

        <h2>Send parking directions?</h2>
        <p>
          Do you want to open an Outlook/email draft with directions for{" "}
          <strong>{prompt.guestName}</strong>?
        </p>

        <div className="directions-box">
          <div><strong>Area:</strong> {prompt.areaName}</div>
          <div><strong>Slot:</strong> {prompt.slotCode}</div>
          <div><strong>Date:</strong> {formatDateLabel(prompt.bookingDate)}</div>
        </div>

        <div className="modal-actions">
          <button className="secondary" onClick={onClose}>No</button>
          <a className="button-link" href={mailtoUrl} onClick={onClose}>
            <Mail size={16} /> Open email draft
          </a>
        </div>
      </div>
    </div>
  );
}

function CancelConfirmDialog({ booking, onConfirm, onClose }) {
  if (!booking) return null;

  const isPrebook = booking.booking_type === "prebook";

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <X size={18} />
        </button>

        <h2>{isPrebook ? "Remove prebooking?" : "Cancel booking?"}</h2>
        <p>
          {isPrebook
            ? "This will release the CEO's default slot for the selected day. It will not be recreated automatically for that day."
            : "Are you sure you want to remove this booking?"}
        </p>

        <div className="directions-box">
          <div><strong>Slot:</strong> {booking.slot_code || "—"}</div>
          <div>
            <strong>{isPrebook ? "Prebooked for" : booking.person_type === "guest" ? "Guest" : "Employee"}:</strong>{" "}
            {booking.person_name}
          </div>
          <div><strong>Type:</strong> {isPrebook ? "Default prebooking" : booking.booking_type}</div>
        </div>

        <div className="modal-actions">
          <button className="secondary" onClick={onClose}>
            {isPrebook ? "Keep prebooking" : "Keep booking"}
          </button>
          <button
            className="danger"
            onClick={() => {
              onConfirm(booking);
              onClose();
            }}
          >
            <Trash2 size={16} /> {isPrebook ? "Yes, release slot" : "Yes, remove"}
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [availability, setAvailability] = useState(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [bookingType, setBookingType] = useState("employee");
  const [selectedPerson, setSelectedPerson] = useState("");
  const [guestName, setGuestName] = useState("");
  const [message, setMessage] = useState(null);
  const [initialError, setInitialError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [guestDirectionsPrompt, setGuestDirectionsPrompt] = useState(null);
  const [cancelConfirmBooking, setCancelConfirmBooking] = useState(null);

  const personName = bookingType === "guest" ? guestName.trim() : selectedPerson;

  useEffect(() => {
    loadAvailability("");
  }, []);

  useEffect(() => {
    const savedPerson = localStorage.getItem("parking_selected_person");
    const savedType = localStorage.getItem("parking_booking_type");

    if (savedType === "employee" || savedType === "guest") {
      setBookingType(savedType);
    }

    if (savedPerson) {
      setSelectedPerson(savedPerson);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("parking_booking_type", bookingType);

    if (bookingType === "employee" && selectedPerson) {
      localStorage.setItem("parking_selected_person", selectedPerson);
    }
  }, [bookingType, selectedPerson]);
  useEffect(() => {
    if (selectedDate) loadAvailability(selectedDate);
  }, [selectedDate]);

  useEffect(() => {
    if (!message) return;

    const timer = setTimeout(() => {
      setMessage(null);
    }, 3000);

    return () => clearTimeout(timer);
  }, [message]);

  async function loadAvailability(dateValue = selectedDate) {
    setLoading(true);

    try {
      const qs = dateValue ? `?booking_date=${dateValue}` : "";
      const data = await api(`/api/availability${qs}`);

      setAvailability(data);
      setSelectedDate(data.booking_date);
      setInitialError(null);
    } catch (err) {
      setMessage({ type: "error", text: err?.message || "Failed to load availability." });
      if (!availability) setInitialError(err?.message || "Failed to load availability.");
    } finally {
      setLoading(false);
    }
  }

  const alreadyBooked = useMemo(() => {
    if (!availability || !personName) return null;

    for (const area of availability.areas) {
      for (const slot of area.slots) {
        if (slot.booking?.person_name?.toLowerCase() === personName.toLowerCase()) {
          return slot.booking;
        }
      }
    }

    return null;
  }, [availability, personName]);

  const totals = useMemo(() => {
    if (!availability) return { total: 0, booked: 0, free: 0 };

    const slots = availability.areas.flatMap((area) => area.slots);
    const booked = slots.filter((slot) => slot.booking).length;

    return {
      total: slots.length,
      booked,
      free: slots.length - booked,
    };
  }, [availability]);

  async function bookSlot(area, slot) {
    if (!personName) {
      setMessage({ type: "error", text: "Please select an employee or enter a guest name." });
      return;
    }

    const info = AREA_INFO[area.area_id] || {};

    try {
      const result = await api("/api/book", {
        method: "POST",
        body: JSON.stringify({
          booking_date: selectedDate,
          slot_code: slot.slot_code,
          person_name: personName,
          person_type: bookingType,
          requested_by: personName,
        }),
      });

      setMessage({ type: "success", text: result.message || "The booking was successfully made." });

      if (bookingType === "guest") {
        setGuestDirectionsPrompt({
          guestName: personName,
          areaName: area.area_name,
          slotCode: slot.slot_code,
          bookingDate: selectedDate,
          mapUrl: info.mapUrl,
          directions: info.directions,
        });
      }

      if (bookingType === "guest") {
        setGuestName("");
      }

      await loadAvailability(selectedDate);
    } catch (err) {
      setMessage({ type: "error", text: err?.message || "Booking failed." });
      await loadAvailability(selectedDate);
    }
  }

  async function cancelBooking(booking) {
    const requestedBy =
      personName ||
      (booking.booking_type === "prebook"
        ? "prebook-removal"
        : booking.person_type === "guest"
          ? "guest-removal"
          : booking.person_name);

    try {
      const result = await api("/api/cancel", {
        method: "POST",
        body: JSON.stringify({
          booking_id: booking.id,
          requested_by: requestedBy,
        }),
      });

      setMessage({ type: "success", text: result.message || "The booking was cancelled." });
      setSelectedPerson("");
      setGuestName("");

      await loadAvailability(selectedDate);
    } catch (err) {
      setMessage({ type: "error", text: err?.message || "Cancel failed." });
    }
  }

  if (!availability) {
    return (
      <main className="page">
        <div className="loading">
          {initialError ? `Could not load parking app: ${initialError}` : "Loading parking app..."}
        </div>
      </main>
    );
  }
  function scrollToBookingPanel() {
    const panel = document.getElementById("booking-panel");

    if (panel) {
      panel.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }
  return (
    <main className="page">
      <GuestDirectionsDialog
        prompt={guestDirectionsPrompt}
        onClose={() => setGuestDirectionsPrompt(null)}
      />

      <CancelConfirmDialog
        booking={cancelConfirmBooking}
        onConfirm={cancelBooking}
        onClose={() => setCancelConfirmBooking(null)}
      />

      {message && (
        <div className={`toast-message ${message.type}`}>
          {message.type === "success" ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="hero">
        <div className="hero-left">
          <div className="hero-top">
            <div className="logo-card">
              <EvoluteLogo className="evolute-logo" />
            </div>

            <h1 className="hero-title">Internal Booking Tool</h1>
          </div>
        </div>

        <div className="hero-actions">
          <button onClick={() => loadAvailability(selectedDate)} disabled={loading}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      <section className="layout">
        <aside className="panel" id="booking-panel">
          <h2>Booking panel</h2>

          <a
            href={RULES_PDF_URL}
            target="_blank"
            rel="noreferrer"
            className="rules-link"
          >
            View parking rules
          </a>

          <label>Date</label>
          <select value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)}>
            {availability.allowed_dates.map((date) => (
              <option key={date} value={date}>
                {formatDateLabel(date)}
              </option>
            ))}
          </select>

          <div className="toggle">
            <button
              className={bookingType === "employee" ? "active" : ""}
              onClick={() => {
                setBookingType("employee");
                setGuestName("");
              }}
            >
              <Users size={16} /> Employee
            </button>

            <button
              className={bookingType === "guest" ? "active" : ""}
              onClick={() => {
                setBookingType("guest");
                setSelectedPerson("");
              }}
            >
              <UserPlus size={16} /> Guest
            </button>
          </div>

          {bookingType === "employee" ? (
            <>
              <label>Employee</label>
              <select value={selectedPerson} onChange={(event) => setSelectedPerson(event.target.value)}>
                <option value="">Select employee</option>
                {availability.employees.map((employee) => (
                  <option key={employee} value={employee}>
                    {employee}
                  </option>
                ))}
              </select>
            </>
          ) : (
            <>
              <label>Guest name</label>
              <input
                value={guestName}
                onChange={(event) => setGuestName(event.target.value)}
                placeholder="Type guest full name"
              />
              <small>Guests can book only non-restricted areas. Guest bookings can be removed by anyone.</small>
            </>
          )}

          {alreadyBooked && (
            <div className="warning">This person already has a booking for this day.</div>
          )}
          {message && (
            <div className={`panel-message ${message.type}`}>
              {message.type === "success" ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
              <span>{message.text}</span>
            </div>
          )}
          <div className="stats">
            <div><strong>{totals.total}</strong><span>Total</span></div>
            <div><strong>{totals.booked}</strong><span>Booked</span></div>
            <div><strong>{totals.free}</strong><span>Free</span></div>
          </div>
        </aside>

        <section className="content">
          <div className="date-title">
            <CalendarClock size={18} /> {formatDateLabel(selectedDate)}
          </div>

          <div className="areas">
            {availability.areas.map((area) => {
              const info = AREA_INFO[area.area_id] || {};

              return (
                <article key={area.area_id} className="area-card">
                  <div className="area-head">
                    <div>
                      <h3 className="area-title">
                        {area.area_name}

                        {info.mapUrl && (
                          <a
                            href={info.mapUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="area-map-icon"
                            title="Open map"
                          >
                            <MapPin size={16} />
                          </a>
                        )}
                      </h3>

                      <p>
                        {area.is_restricted
                          ? `Restricted: ${area.allowed_users.join(", ")}`
                          : "Open area"}
                      </p>
                    </div>

                    <span>
                      {area.slots.filter((slot) => !slot.booking).length}/{area.slots.length} free
                    </span>
                  </div>

                  <div className="slots">
                    {area.slots.map((slot) => {
                      const disabled =
                        !personName ||
                        !!alreadyBooked ||
                        !!slot.booking ||
                        (area.is_restricted && bookingType === "guest") ||
                        (area.is_restricted &&
                          bookingType === "employee" &&
                          !area.allowed_users.includes(selectedPerson));

                      const isOwn =
                        slot.booking?.person_name?.toLowerCase() === personName.toLowerCase();

                      const isGuestBooking = slot.booking?.person_type === "guest";
                      const isPrebook = slot.booking?.booking_type === "prebook";
                      const canRemove = isPrebook || isOwn || isGuestBooking || personName === "admin";

                      return (
                        <div
                          key={slot.slot_code}
                          className={`slot ${slot.booking ? "booked" : "free"} ${isOwn ? "own" : ""}`}
                        >
                          <div className="slot-title">
                            <CircleParking size={17} />
                            <strong>{slot.slot_code}</strong>
                          </div>

                          {slot.booking ? (
                            <>
                              <div className="booking-name">
                                {isPrebook
                                  ? "Prebooked for"
                                  : slot.booking.person_type === "guest"
                                    ? "Book for"
                                    : "Booked by"}:{" "}
                                {slot.booking.person_name}
                              </div>

                              <div className="booking-type">
                                {isPrebook ? "Default prebooking" : slot.booking.booking_type}
                              </div>

                              <button
                                className="danger"
                                disabled={!canRemove}
                                onClick={() =>
                                  setCancelConfirmBooking({
                                    ...slot.booking,
                                    slot_code: slot.slot_code,
                                  })
                                }
                                title={
                                  isPrebook
                                    ? "Release the default CEO prebooking for this day"
                                    : isGuestBooking
                                      ? "Guest bookings can be removed by anyone"
                                      : "Only owner or admin can remove employee bookings"
                                }
                              >
                                <Trash2 size={15} /> {isPrebook ? "Remove prebooking" : "Remove booking"}
                              </button>
                            </>
                          ) : (
                            <>
                              <div className="booking-name">Available</div>
                              <button disabled={disabled} onClick={() => bookSlot(area, slot)}>
                                Book slot
                              </button>
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      </section>
      <div
        className="mobile-booking-bar"
        onClick={scrollToBookingPanel}
      >
        <div>
          <span>Date</span>
          <strong>{formatDateLabel(selectedDate)}</strong>
        </div>

        <div>
          <span>{bookingType === "guest" ? "Guest" : "Employee"}</span>
          <strong>
            {personName || "Not selected"}
          </strong>
        </div>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);