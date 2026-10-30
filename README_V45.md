# Ashkan Hotel Pro v45 — Indicative Stay KPIs

Adds a branch-authorized bilingual Excel report for estimated accommodation value, indicative ADR and indicative RevPAR. Uses saved `booking_rates` quotes, prorated evenly by overlapping stay nights. **Not recognized revenue, not an accounting P&L, and not a reliable historical capacity measure**. Missing quotes produce blank ADR/RevPAR to avoid presenting misleading results. Excludes cancelled reservations. Uses current active-room count as capacity proxy. No database schema changes. UI export is on Branch Reports.

Run: `py -m pip install -r requirements.txt`, then `py main.py`. Tests: `py -m unittest discover -s tests -v`. Back up hotel.db before upgrades.
