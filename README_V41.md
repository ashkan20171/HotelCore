# Ashkan Hotel Pro v41

## Branch reporting CSV export

The Branch Analytics page now provides an **Export Excel CSV** button. It exports reservations for the selected branch and inclusive date range, enforcing the existing branch authorization before querying. Files use UTF-8 with BOM for Excel and escape potentially dangerous spreadsheet formulas. Column headers follow the active Persian or English UI language. Stored data and database schema are unchanged.

Run: `py -m pip install -r requirements.txt`, then `py main.py`.
Tests: `py -m unittest discover -s tests -v`.

Note: CSV is Excel-compatible but is not a native `.xlsx` workbook. Backup `hotel.db` before upgrading.
