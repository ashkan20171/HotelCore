# Stage 158 — Booking creation pace

Adds booking creation pace for the selected 7–90-day horizon, comparing consecutive equal-length periods by `reservations.created_at`. Includes subsequently cancelled bookings; this is **booking creation activity**, not net bookings, booked occupancy, realized revenue or a statistical forecast.

- Authorized, read-only SQLite aggregate with bound dates.
- Bilingual summary and daily creation counts in Booking Outlook.
- Threshold-based low booking creation activity and 25% decline indicators.
- No guest personal data in the pace result.
- Run tests: `python -m unittest discover -s tests -q`.
- Windows PySide6 GUI still requires manual visual validation.
