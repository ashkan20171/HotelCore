# Ashkan Hotel Pro — Stage 168

## Security report improvements
- Added a validated `security_event_detail(conn, event_id)` service function for safe, parameterized retrieval of one authentication event.
- Added a bilingual event-details dialog, opened by double-clicking a row in the security report.
- Replaced ambiguous sentinel-date behavior with explicit “From date” and “To date” checkboxes; date controls are enabled only when their filter is active.
- Preserved the existing CSV export protections and existing permission/session check in the main window entry point.

## Validation
Run from the project directory:

```bash
python -m unittest discover -s tests -q
```

The optional PySide6 GUI requires PySide6 installed in the target environment. If PySide6 is unavailable, pure service functions and unit tests remain usable; GUI interaction cannot be visually tested in that environment.
