# Ashkan Hotel Pro v97 — Multi-property insights

- Admin-only multi-property dashboard adds branch name search, KPI ranking and alerts-only filtering.
- Relative bar visualization for up to 12 displayed branches; ranking remains available for all authorized branches.
- PDF export of currently filtered rows with date window, explicit indicative-not-recognized-revenue caveat, and no guest PII.
- PDF uses ReportLab (installed from `requirements.txt`). PDF text is English for portability; the application UI remains bilingual.
- Branch authorization and scorecard aggregation are unchanged from v96.
- All reported inventory is current inventory, not historical; room-rate allocations are estimates.

Back up hotel.db before upgrading. Run `py -m pip install -r requirements.txt` then `py main.py`.
