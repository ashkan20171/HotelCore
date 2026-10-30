# Ashkan Hotel Pro v63 — Alert Severity Filters

Adds critical/high/medium classifications and a severity dropdown to the authorized Branch Analytics alert table. Critical means amount >= 3× configured threshold; high >= 2×; medium otherwise. When threshold is zero, all alerts are high. Severity filters affect the alerts table, not the financial totals or authorization. Persian/English labels. Pure classification rules in `branch_alert_priority.py` with 12 unit tests.

Run `python -m unittest discover -s tests -q` and `python main.py` after installing `requirements.txt`. Windows GUI still requires manual integration testing. Back up `hotel.db` before upgrades.
