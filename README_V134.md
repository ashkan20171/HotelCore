# Stage 134 — Occupancy Visualization and Management Alerts

- Added daily **reservation-based** occupancy line chart, counting distinct room IDs so duplicate/overlapping bookings do not inflate occupancy above 100%.
- Added deterministic management alerts for low reservation occupancy (<30%), expenses >=90% of receipts, and receipts down >20% from the previous period.
- Read-only, bounded 90-day occupancy query runs inside the existing authorized dashboard worker.
- Added bilingual Persian/English labels. No branch filtering: the existing dashboard is not branch-scoped; adding a fake filter would be misleading.
- **Limitations:** This is booked occupancy, not verified physical stays; alerts are indicative, not forecasts. Persian PDF font support remains pending. Back up hotel.db and validate UI on Windows.
