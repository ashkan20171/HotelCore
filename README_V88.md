# Ashkan Hotel Pro v88 — Executive Branch Dashboard

The room-transfer history now opens a bilingual executive dashboard with four KPI cards, authorized branch comparison, search by branch, sortable metrics, per-branch progress bars and filtered CSV export. A separate pure transformation module (`transfer_executive_dashboard.py`) keeps UI presentation separate from authorization and SQL data access.

The **unique booking** and **active staff** KPI cards sum *per-branch counts*; they do not deduplicate users or bookings across different branches. Admin-only multi-branch restrictions remain enforced in `transfer_branch_comparison.py`. No guest PII is exposed.

Run `py -m pip install -r requirements.txt` and `py main.py`. Back up `hotel.db` before updating. The Windows PySide6 GUI still needs manual testing.
