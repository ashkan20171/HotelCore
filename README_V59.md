# Ashkan Hotel Pro v59 — Branch comparison PDF

- New **Export Branch Comparison PDF** action in Branch Analytics.
- Uses the **same authorized, filtered and sorted rows** as the comparison table, CSV and Excel.
- Includes the reporting period, visible branch count, per-branch amounts, totals, and cash-movement disclaimer.
- Supports Persian/English with Unicode TTF fonts; no database migration.
- `branch_comparison_pdf.py` separates validation and PDF rendering from the GUI.
- `python -m unittest discover -s tests -q` to run tests.

**Note:** ReportLab, arabic-reshaper, python-bidi and a compatible Unicode TrueType font are required for Persian PDF. Verify output on Windows. Back up `hotel.db` before upgrading.
