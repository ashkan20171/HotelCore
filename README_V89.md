# Ashkan Hotel Pro v89 — Revenue & Occupancy Dashboard

Adds a dedicated bilingual dashboard launched from the main management dashboard. Choose 7/30/90 days to see **indicative** occupancy, ADR, RevPAR, estimated accommodation value, warnings about missing quotes and overcapacity, and Excel export. All metrics are scoped to the authenticated user's active branch through existing `estimated_branch_performance` authorization.

**Important:** These are estimates derived from reservation quotes allocated across booked nights and current active room inventory; they are **not recognized revenue**, and historical inventory snapshots are not available. ADR/RevPAR are hidden if booking quotes are missing. This is not a cash receipt report.

Install dependencies with `py -m pip install -r requirements.txt` and run `py main.py`. Back up `hotel.db` before updating. PySide6 UI needs manual Windows verification.
