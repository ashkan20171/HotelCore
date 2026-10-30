# Stage 141 — Accurate occupancy and polished Excel reporting

- Executive occupancy KPI now counts **distinct room/day combinations** when reservations contain room_id, preventing duplicate occupancy from overlapping bookings. Legacy schemas without room_id use the previous calculation for compatibility.
- Cancelled reservations and reservations for missing room records do not contribute to occupancy.
- Excel exports now include styled headers, alternating row backgrounds, numeric formats, freeze panes, filters, fitted page width and readable column widths.
- Daily activity tab now supports date substring filtering alongside existing sorting and day details.
- All controls retain Persian RTL and English LTR labels.

Run `python -m unittest discover -s tests -q`.

Limitations: occupancy is reservation-based, not physical check-in; receipts and expenses are not accrual accounting; GUI needs Windows smoke testing.
