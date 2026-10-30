# Stage 131 — Executive Dashboard

Adds a bilingual, read-only management dashboard with period comparison, recorded payments and expenses, reservation counts, room-night occupancy, and daily receipts/costs. Accessible from **User & Role Management → System Health → Executive Dashboard** with `security.view` authorization.

## Definitions and limitations
- **Occupancy** = reserved, non-cancelled room-nights divided by total room-nights for the period, using check-in inclusive and checkout exclusive. It is *booking-based*, not physical occupancy. Overlapping bookings may overstate occupancy.
- **Receipts** are sums of recorded payments, not recognized revenue; **cash difference** is receipts minus recorded expenses, not net profit. Currency units follow database values.
- **Comparison** uses the immediately preceding equal-length period.
- Date filters use UTC for financial timestamps and calendar dates for stay-night overlap.
- Database queries run in a Qt worker; no GUI objects are accessed from the worker.
- This is not an accounting-grade ledger or a production-validated revenue system. Test the GUI on Windows and back up hotel.db before upgrading.

## Tests
`python -m unittest discover -s tests -q`
