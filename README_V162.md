# Ashkan Hotel Pro — Stage 162

## Reservation audit timeline UI

Stage 162 adds a PySide6 dialog for browsing the append-only reservation audit trail introduced in Stage 161. The dialog is reachable from the Reservations page through **Reservation audit history** (administrator-only).

Features:
- Filters by reservation ID, event type (created/updated/deleted), and date range.
- Displays the newest matching events first, capped at 500 rows per query.
- Selecting an event shows its metadata and before/after snapshots as readable JSON.
- Persian and English labels; dates are explicitly identified as UTC.
- Validates reservation IDs and date ranges before querying.
- Uses bound SQL parameters for user-supplied filters.

## Important limitations

- The current database triggers still record the actor as `database-trigger`; this UI does not claim to identify the signed-in employee for each write.
- Access to the full audit history is restricted in the UI to the administrator role. For deployment-grade authorization, the audit query should also be enforced in the service/security layer rather than relying solely on a hidden button.
- The audit trail captures reservation fields only; it intentionally excludes guest names, phone numbers, and national IDs.
- PySide6 is not installed in this build environment, so the GUI could not be launched for visual/manual interaction testing here. Run the app on the target Windows environment to verify layout and date widgets.

## Validation

Run the complete suite with:

```bash
python -m unittest discover -s tests -q
```
