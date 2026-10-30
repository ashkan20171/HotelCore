# Ashkan Hotel Pro v103 — Session Security & Login Audit

New `security_sessions.py` provides SQLite-backed opaque random sessions with SHA-256 token digests, 12-hour expiry, explicit revocation, last-activity metadata and login history without passwords or guest data.

- Active admins can review recent login outcomes, list user sessions and revoke a user's sessions.
- Disabling an account, changing its role, or resetting its password revokes all sessions.
- Main navigation checks that the current session is active before opening a new page.
- A session is revoked when the application exits normally.
- `user_access_management.py` continues to enforce admin-only mutations.
- Tests cover expiration, revocation, authorization and audit.

**Limitations:** This is not a complete request-level permission framework: actions on an already-open page may need further authorization checks. The main window must be tested on Windows 11; this build is a development/portfolio release. The session token remains in application memory only.
