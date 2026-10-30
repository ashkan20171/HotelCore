# Stage 159 — Gross/net booking pace and cancellation cohort analysis

- Authorized read-only cohort aggregation of reservations by creation date.
- Compares gross created bookings, currently cancelled bookings, and net active bookings across equal-length periods.
- Customizable thresholds for net booking rate, decline, and cancellation share.
- Interactive bilingual chart (gross amber, net teal) with hover details.
- **Limitation:** cancellations are attributed to original booking creation date and current status, **not** cancellation event date. This is not an event-time cancellation trend or a demand forecast.
- Run tests: `python -m unittest discover -s tests -q`.
- Windows PySide6 GUI still requires manual validation.
