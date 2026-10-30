# Stage 127 — Report Center & GitHub presentation

- New `report_center_v127.py`: admin-authorized SQLite audit trail for system health report exports.
- Tracks UTC time, PDF/XLSX format, outcome, filename (basename only), record count and sanitized error category.
- Search and filter by filename, status and format; capped query results and indexed newest-first ordering.
- Integrated a Report Center table and filters into the System Health dialog.
- Logs success, cancellation and failures without changing the export's own result if audit recording fails.
- New `tests/test_report_center_v127.py` validates filtering, input constraints and permission checks.
- Added `README_GITHUB.md` for international recruiters.

**Scope:** Audit history is created only for new exports made after this upgrade. It does not retroactively recover prior exports or automatically replay past reports. GUI behavior requires Windows verification.
