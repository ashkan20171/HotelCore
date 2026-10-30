# Ashkan Hotel Pro v56 — Branch search and safe CSV exports

- Search branch comparison results by name, with Unicode-normalized case-insensitive matching.
- Only previously authorized branches are queried; the search never broadens permissions.
- Export the **currently filtered and sorted** cash movement comparison as UTF-8 CSV.
- CSV export protects against spreadsheet formula injection in branch names.
- Filtering applies to both the comparison table and visual comparison bars.
- Added unit tests in `tests/test_branch_report_filters.py`.
- Cash movement is not accrual profit and loss. Back up `hotel.db` before upgrade.
