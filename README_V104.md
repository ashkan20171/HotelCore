# Ashkan Hotel Pro Enterprise v104

## Security dashboard
The existing **Users & Roles** page now displays a six-card security overview: successful, failed and locked login attempts over the previous seven days (UTC), currently valid sessions, disabled accounts and total accounts. A recent security-change table includes actor, target and event metadata but never passwords or session tokens.

## Permission checks
`security_overview.py` introduces `require_permission` and explicit permission identifiers. Navigation rechecks the user's **current** role and active state against SQLite instead of trusting the role cached at sign-in. Existing branch-level authorization and service checks remain in place.

## Limitations and next steps
This is not yet a full end-to-end authorization audit. Some callbacks in already-open pages require service-level session validation, and fine-grained permissions are role-defined rather than independently configurable. The GUI must be smoke-tested on Windows 11. Back up `hotel.db` before updating.

Run `py -m unittest discover -s tests -q`.
