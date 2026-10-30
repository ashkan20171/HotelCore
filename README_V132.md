# Stage 132 — Executive visual analytics and room-type value estimates

- Bilingual dark-background Qt trend chart of recorded receipts and expenses.
- Room-type breakdown of booked nights, **estimated booked value**, estimated ADR and estimated RevPAR.
- Estimates use room list rates multiplied by non-cancelled booked nights; **they are not recognized revenue, actual ADR, or accounting RevPAR**. No discounts, refunds, commissions, room closures, tax or dynamic rates are modeled. Overlapping bookings can inflate metrics.
- Uses the existing authorized background dashboard worker and existing 1–90 day selector. No external plotting library required.
- SQLite data is read-only. Tests: `python -m unittest discover -s tests -q`.
- Verify visual behavior on Windows before production use. Back up `hotel.db` before upgrading.
