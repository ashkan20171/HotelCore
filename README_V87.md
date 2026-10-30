# Ashkan Hotel Pro v87 — Authorized branch transfer comparison

The room-transfer history dialog now includes a **Compare branches** view, with branch-level transfer counts, unique reservations, distinct source/destination rooms, active staff and most frequent actor. It respects the selected report date range and provides UTF-8 CSV export.

**Security:** comparison is restricted to active branches authorized for the signed-in user; only administrators may compare multiple branches. No guest personal data is included. Reports are read-only.

Run `python -m pip install -r requirements.txt`, then `python main.py`. Back up `hotel.db` before upgrading. UI needs manual testing on Windows with PySide6.
