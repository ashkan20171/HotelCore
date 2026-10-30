# Ashkan Hotel Pro v49 — Period-over-period branch cashflow KPIs

The Branch Analytics page now includes an in-app comparison of the selected period against the immediately preceding period of equal duration. Receipts, allocated expenses and net cash movement are compared with percentage deltas. When the previous amount is zero, an undefined percentage is shown as **new** instead of dividing by zero.

The comparison uses the existing branch-scoped `cashflow` function twice with the same user/role/branch, preserving branch authorization. Persian/English labels follow the selected UI language. This is a cash-movement comparison, **not** accrual profit and loss.

Install: `py -m pip install -r requirements.txt` then `py main.py`. Back up `hotel.db` before updating.

Run tests: `py -m unittest discover -s tests -q`.
