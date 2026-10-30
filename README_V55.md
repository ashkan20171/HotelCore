# Ashkan Hotel Pro v55 — Saved report preferences and branch sorting

- Branch report preferences (date range, authorized branch, sort field, sort direction) are stored per user using QSettings.
- Preferences store only UI choices, **never** monetary figures or private reports.
- Previously selected branch is restored only if still present in the authorized branch list.
- Branch cashflow table and visual comparison share the same configurable ordering: receipts, expenses, net movement, or branch name; ascending/descending.
- Sorting is pure and covered by nine unit tests in `tests/test_branch_sorting.py`.
- Persian RTL / English LTR and Jalali date selection are preserved.
- Back up `hotel.db` before upgrading; no database schema change in v55.
- Cash movement is not accrual profit-and-loss reporting.
