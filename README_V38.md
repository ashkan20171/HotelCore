# Ashkan Hotel Pro v38 — Dashboard Insights

- Refreshed monthly revenue chart with gradient bars and safe nonnegative heights.
- Branch-scoped occupancy guidance, in Persian (default) or English.
- Month-over-month revenue comparison using only available branch payment data.
- Extracted `dashboard_insights.py` pure functions and added 9 tests.
- No database schema changes. Copy `hotel.db` from the previous version after backup.
- Run: `py -m pip install -r requirements.txt` then `py main.py`.
- Tests: `py -m unittest discover -s tests -v`.
- Limitation: graphical Windows testing and complete translation of legacy dialogs are pending.
