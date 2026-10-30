# Ashkan Hotel Pro v46 — Branch Cash Movement

Introduces a dedicated branch-expense ledger (`branch_expenses`) and branch-authorized cash-movement reporting/export. Record an expense in Branch Reports, then export an Excel workbook for the selected branch and period. Dates use half-open intervals, with an inclusive UI end date. Recorded payments are cash receipts, not earned revenue; recorded branch expenses are cash outflows, not accrual expenses. **This is NOT a profit-and-loss statement.** Legacy expenses without branch assignments are intentionally excluded. New expenses are stamped with the user and entry timestamp; original legacy tables are not modified. Back up `hotel.db` before upgrading.

Run `py -m pip install -r requirements.txt` then `py main.py`; tests `py -m unittest discover -s tests -v`.
