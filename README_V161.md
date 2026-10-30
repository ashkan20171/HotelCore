# Ashkan Hotel Pro Enterprise — Stage 161

## Booking audit trail

Stage 161 adds an append-only SQLite audit table for reservation lifecycle events. Database triggers record reservation creation, meaningful updates, and deletion, including UTC event timestamps and before/after snapshots of room ID, guest ID, stay dates, status, and the original `created_at` value. No guest name, phone, or national ID is copied into the audit snapshot.

### Developer API

```python
from booking_audit_v161 import install, reservation_timeline, recent_events

# Called by the application startup migration in main.init().
install(connection)  # idempotent
history = reservation_timeline(connection, reservation_id=42, limit=100)
latest = recent_events(connection, limit=50)
```

`reservation_timeline` validates IDs and limits and parses snapshot JSON. Triggers ensure changes made through direct SQL are captured too, not only those routed through a particular UI form.

## Important attribution limitation

Events currently identify the actor as `database-trigger`. SQLite triggers cannot infer the authenticated application username. Accurate per-user attribution requires passing an authenticated actor context through every write connection or changing reservation write services to set it explicitly; the app must not claim that this stage identifies individual users. Event timestamps are UTC.

## Validation

Run `python -m unittest discover -s tests -q`. The new tests cover idempotent migration, create/update/delete capture, no-op updates, timeline ordering, and input validation. A successful automated test run does not replace visual testing of the PySide6 interface on Windows.
