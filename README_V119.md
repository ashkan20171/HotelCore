# Ashkan Hotel Pro — Stage 119: System Health Dashboard

An administrator-only, on-demand system-health dialog is available from the User & Role Management page. It reports SQLite `PRAGMA quick_check(1)` status, current in-process security-monitor worker state, persisted monitor failure count, and the most recent healthy check. Each explicit check is persisted with a 500-entry retention cap; the last 20 checks appear in the dialog.

The health panel requires an authorized `security.view` session. It does not send network telemetry, and a successful quick check is **not** a substitute for full integrity checks or backups. No operating-system resource or remote-service health checks are claimed.

Run: `python -m unittest discover -s tests -q`
