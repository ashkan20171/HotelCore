# Ashkan Hotel Pro v64 — Multi-Branch Monthly Trend and Alert Preferences

- Added a multi-branch monthly cashflow summary table, built exclusively from the already authorized and filtered branches; monthly totals include receipts, expenses and net cash movement.
- Saved the alert-severity filter per report user in QSettings.
- Reorganized executive KPI tiles into a three-column grid to reduce horizontal overflow on smaller windows.
- Pure validation and aggregation in `branch_trend_summary.py` with dedicated tests.
- No database migration. Back up `hotel.db` before replacing files.
- Run `python -m unittest discover -s tests -q` and `python main.py` after installing requirements.
- GUI needs manual verification on Windows with PySide6.
