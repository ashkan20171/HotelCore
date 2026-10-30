# Ashkan Hotel Pro — Stage 165

## Authentication security event log

Stage 165 adds an append-oriented `login_security_events` table to `login_security.py` and records authentication outcomes from `authenticate_user`:

- `failure`: supplied credentials were invalid or the account was inactive.
- `locked`: the account is currently under a login lockout.
- `success`: authentication succeeded.

The event record stores only a bounded attempted username, outcome, UTC timestamp, and a short fixed-category detail. Passwords, password hashes, salts, session tokens, and submitted credential text are never passed to the event logger. Existing lockout counters and session login history remain in place.

`recent_security_events(conn, limit=100, outcome=None)` returns validated, newest-first records for an administrator-facing report. This stage adds the recording API and authentication integration; it does not yet add a dedicated UI screen or network/IP fingerprinting. SQLite table access control still depends on operating-system and application deployment security.

## Tests

Run `python -m unittest tests.test_login_security_events_v165 -v` or the full suite with `python -m unittest discover -s tests -q`.
