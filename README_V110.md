# Ashkan Hotel Pro v110 — Security PDF & Trends

- Admin-only UTC daily login trends for the selected 1–90 day period.
- PDF report with daily success/failure/locked counts, totals, and accounts flagged for review.
- Persian/English PDF labels, with optional installed Arabic reshaping and Unicode fonts.
- PDF export action integrated into Login Activity Analytics dialog.
- Existing user, session, and operation permission checks retained.

## Run
`py -m pip install -r requirements.txt`

`py -m unittest discover -s tests -q`

`py main.py`

Back up `hotel.db` before upgrading. The PySide6 GUI has not been smoke-tested on Windows. This is not a production-certified security monitoring system.
