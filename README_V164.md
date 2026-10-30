# Stage 164 — Authenticated reservation audit actor

- SQLite audit triggers now call the connection-local `booking_audit_actor()` function instead of hard-coding `database-trigger`.
- `booking_audit_v161.set_current_actor(username)` sets a validated execution-context actor; invalid/blank values fall back to `database-trigger`.
- `main.connect()` registers the SQLite function and the authenticated main-window username is set when `Main` is constructed.
- `install()` is idempotent and recreates the three triggers to migrate existing installations from hard-coded actor values.
- Tests cover actor attribution on insert/update, fallback validation and idempotent installation.

## Security / scope notes

The actor label is the authenticated username available to the current UI execution context. This is not a cryptographic proof of identity, and code that opens separate SQLite connections outside `main.connect()` must call `register_actor_function(conn)` (the installer does so for connections used during migration). The audit trail remains an operational audit mechanism, not tamper-proof storage against a database administrator. The actor value is not retroactively applied to older events.
