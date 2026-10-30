# Stage 135 — Configurable Executive Alerts

- Three per-admin configurable percentage thresholds: low booked occupancy, expenses/receipts, receipts decline against previous period.
- Settings are stored in SQLite `executive_alert_preferences`, isolated by admin ID, with parameterized statements and CHECK constraints.
- Existing `security.view` authorization is required to save; dashboard worker reads preferences after authorization.
- Defaults: 30%, 90%, 20%. Values validated as integer percentages 0–100.
- Bilingual settings controls in the existing executive dashboard; refreshes alerts after saving.
- Limitations: no branch-scoped reporting, PDF Persian Unicode support still pending; GUI needs Windows testing. Back up hotel.db before upgrading.
