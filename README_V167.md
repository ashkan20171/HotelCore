# Ashkan Hotel Pro — Stage 167

## Security event report integration

- Added an admin-visible sidebar shortcut for the security event report.
- The report entry point requires a non-null user ID and active session token.
- Immediately before opening the report, it calls `authorize_action(..., 'security.view')`, which revalidates the session and current database permission.
- Reuses the Stage 166 report dialog and its filtered CSV export. The dialog uses the active application language (Persian/RTL or English/LTR through the existing application language conventions).
- Handles permission/session/database/UI availability errors with a user-facing warning.

## Validation

Run the project tests with:

```bash
python -m unittest discover -s tests -q
```

The GUI cannot be visually launched in environments without PySide6; test the actual sidebar and dialog on the target Windows/PySide6 installation as part of release validation.
