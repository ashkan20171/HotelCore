# Ashkan Hotel Pro v58

- Visible-branch financial totals computed **after** authorized search, advanced filtering and sorting.
- Financial filter preferences persisted per user and role via QSettings.
- One-click reset for search and financial filters.
- Added nine pure-function tests for totals, formatting and invalid values.
- No database schema changes. The totals are cash movements, **not accrual profit**.
- Backup hotel.db before upgrading. Run `python -m pip install -r requirements.txt` and `python main.py`.
