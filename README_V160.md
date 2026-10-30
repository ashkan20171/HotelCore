# Stage 160 — Cancellation analysis by room type

- Authorized read-only aggregation of booking creation cohorts by room type (`rooms.kind`).
- Displays gross, currently cancelled, net, and cancellation share in bilingual executive dashboard.
- CSV export with formula-injection mitigation and authorization re-check.
- No guest-identifying fields exported.
- **Important:** existing schema stores `created_at` and current status, but does **not** contain reliable cancellation event timestamps. This release **does not** claim to reconstruct cancellation history. Adding a genuine audit timeline requires instrumenting all reservation mutation paths, schema migrations, and legacy-data handling.
- Manual GUI validation on Windows still required.
- Tests: `python -m unittest discover -s tests -q`.
