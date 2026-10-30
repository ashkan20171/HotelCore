# Ashkan Hotel Pro v47 — Branch Cash Movement Dashboard

Adds branch-scoped on-screen cash movement cards and an authorized multi-branch comparison table in the Branch Reports page. Values are recorded receipts minus allocated branch expenses, **not** accounting profit or recognized revenue. Date range is inclusive in the UI and converted to a half-open interval in SQL. Persian RTL / English LTR supported. No database schema changes in this version.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Tests
`py -m unittest discover -s tests -q`

Back up `hotel.db` before upgrading. Windows GUI testing is still required.
