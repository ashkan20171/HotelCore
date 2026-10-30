# Stage 166 — Security administration report

Adds `security_admin_panel_v166.py` with a filtered reporting service and an optional PySide6 `SecurityAdminPanel` dialog for login security telemetry from `login_security.py`.

Features:
- Filter by outcome, attempted username, and inclusive ISO date range.
- Summary counts for failure, locked, and successful logins within active filters.
- UTF-8-BOM CSV export (Persian or English headers).
- Spreadsheet formula-injection mitigation for cells beginning with `=`, `+`, `-`, `@`, tab, or carriage return.
- SQL parameters are bound; username wildcard characters are escaped.

The dialog is provided as a standalone component and is not wired into the main navigation in this stage. PySide6 is optional for the test environment; when absent, service and CSV functions remain usable and instantiating the dialog raises a clear RuntimeError. Authentication event data depends on the integration added in stage 165; this report does not make the SQLite database tamper-proof.
