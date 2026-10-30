# Ashkan Hotel Pro v102 — user access management

Adds active/disabled accounts, role updates (admin/reception), password reset by an active administrator, and metadata-only security event logs. The management page is under Users & Roles (admin only). Disabled accounts cannot authenticate. A self-disable or self-demotion is blocked, and the last active admin is protected.

Passwords are hashed using salted PBKDF2-SHA256 (240,000 iterations). The reset dialog uses hidden password fields. Admin changes are checked in service methods, not just the UI.

**Limits:** this is a basic two-role RBAC system; not a complete fine-grained permission matrix. Existing login sessions are not revoked when an account is disabled; logout/restart is needed. Use a database backup before upgrading.

Run: `py -m unittest discover -s tests -q`
