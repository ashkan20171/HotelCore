# Ashkan Hotel Pro — v40

## Changes
- Interactive dashboard revenue window (7, 30, or 90 days) with inclusive dates.
- Branch-isolated payment totals and comparison against the immediately preceding equal-length period.
- Accessible occupancy progress indicator with Persian/English labels.
- Pure reporting logic in `dashboard_reporting.py` and 11 unit tests.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
py -m unittest discover -s tests -v
```

**Data safety:** Back up `hotel.db` before upgrading. Payment windows use the payment creation date. Period-over-period percentage is omitted when the previous period has zero revenue. GUI testing on Windows remains required.
