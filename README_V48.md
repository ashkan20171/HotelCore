# Ashkan Hotel Pro v48

Adds a monthly cash movement comparison inside Branch Reports, with receipts (teal), allocated expenses (gold) and net movement. Date ranges are inclusive in the UI and exclusive internally; partial months are shown accurately. Queries use the existing branch authorization guard. This is not accrual profit/loss.

Run: `py -m pip install -r requirements.txt` then `py main.py`. Tests: `py -m unittest discover -s tests -q`. Back up hotel.db before upgrading.
