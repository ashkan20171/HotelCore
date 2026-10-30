# Stage 133 — Executive dashboard export

- Adds Excel and PDF export actions to the authorized executive dashboard, with two Excel worksheets: room-type performance and daily receipts/expenses.
- Export controls remain disabled until the authorized background worker returns data; no additional unguarded database queries are made.
- Atomic export writes to a temporary sibling file and replaces the destination only on successful generation.
- Excel formula injection protection for text fields.
- PDF uses ASCII fallback for non-ASCII room type names; Persian PDF fonts need separate configuration.
- Existing room occupancy and estimated ADR/RevPAR remain booking-based estimates; not recognized revenue.
- Branch filter is not included in this stage because this dashboard's schema has no reliable per-branch mapping for all finance tables. Do not assume multi-property financial separation.
- Back up hotel.db and test UI on Windows before deployment.
