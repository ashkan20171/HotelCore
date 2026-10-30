# Ashkan Hotel Pro v106 — user administration polish and privileged action guards

- User management adds searchable account table and compact active/disabled/admin counts.
- Persian RTL and English LTR labels remain supported.
- New `security_action_service.execute_admin_action` rechecks the live session and current admin permission at the moment of sensitive account changes and session revocation.
- Mutations and security events run inside the same caller-managed SQLite transaction.
- Login history and session dialog entry points recheck authorization.
- Pure presentation helpers can be tested without PySide6.

**Limits:** This release does not provide a full fine-grained role editor, nor a complete audit of every existing legacy callback. UI rendering has not been tested on Windows. Back up hotel.db before replacing an existing installation.
