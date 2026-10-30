# Ashkan Hotel Pro v93 — Revenue Dashboard UX

- Scrollable bilingual revenue dashboard with consistent spacing and RTL/LTR.
- Qt-painted occupancy trend (no matplotlib dependency), with 0–100% grid, date labels and empty-state.
- Improved comparison table readability.
- No database schema migration. Back up `hotel.db` before upgrading.
- Metrics remain booking-quote estimates; not recognized accounting revenue.
- Run: `py -m pip install -r requirements.txt` then `py main.py`.
