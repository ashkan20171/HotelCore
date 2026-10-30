# Ashkan Hotel Pro v90 — Occupancy Trends and Period Comparison

The Revenue & Occupancy dashboard now displays daily occupied room counts, occupancy percentages, and the percentage-point change in occupancy against an equal-length preceding period. Calculations are branch-authorized and exclude cancelled bookings.

These are **indicative** figures: historical room inventory is not snapshotted, all currently active rooms define capacity, and reservation quotes do not represent recognized revenue. The comparison uses half-open date ranges. No database schema changes or user data are bundled.

Run `py -m pip install -r requirements.txt`, then `py main.py`. Verify GUI on Windows and back up `hotel.db` before upgrade.
