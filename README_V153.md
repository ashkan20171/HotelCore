# Stage 153 — Room-type booking performance dashboard

- New room-type comparison chart in Executive Dashboard with selectable estimated ADR, estimated RevPAR, booked occupancy and estimated booked value.
- Weighted room-type KPI summary based on available room-nights and booked room-nights, not an average of per-type ratios.
- Read-only chart tooltips, bilingual Persian RTL / English LTR UI, pure analytics helpers and unit tests.
- `available_days` is now exposed in room-value analytics for transparent weighted capacity calculation.

**Accounting disclaimer:** These are booking-based estimates calculated using room rate and reservation overlap; they are **not recognized revenue, profit, realized ADR, or realized RevPAR**. The system does not allocate operational costs to room types.

Run: `python -m unittest discover -s tests -q`; launch: `python main.py` after installing requirements. Windows GUI validation remains necessary.
