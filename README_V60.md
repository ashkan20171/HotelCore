# Ashkan Hotel Pro v60 — Executive Branch KPIs

The Branch Analytics page now includes five management KPI tiles derived **only** from authorized, currently filtered branch cashflow rows: visible branch count, positive/negative net branch counts, average net cash movement per visible branch, and receipts-to-expenses percentage. The tiles update with the existing search, amount/status filters and sorting; they clear on a query error. Zero expense totals yield N/A rather than division by zero. Persian RTL and English LTR captions are supported.

No database migration. Back up `hotel.db` before upgrading. These are cash-movement indicators, not accrual profit or profitability margins. GUI rendering requires manual Windows/PySide6 testing.

Run: `python -m unittest discover -s tests -q` and `python main.py`.
