# Ashkan Hotel Pro v86 — Transfer Analytics

Adds an in-app, read-only, four-tab analytics panel to the room transfer history dialog: monthly trends, staff activity, source rooms, and destination rooms. Bar indicators use Qt progress bars. The model aggregates only the already filtered and branch-authorized transfer records; no schema migration or external requests.

Run: `python -m pip install -r requirements.txt` then `python main.py`. Tests: `python -m unittest discover -s tests`. UI must be verified on Windows with PySide6 installed. Back up `hotel.db` before updating.
