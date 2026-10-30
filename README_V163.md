# Ashkan Hotel Pro Enterprise — Stage 163

## Reservation audit CSV export

The administrator-only reservation audit dialog now has an **Export CSV** action. It exports the currently displayed, filtered events rather than silently fetching a wider dataset. The export includes event/reservation IDs, event type, UTC timestamp, actor, and before/after snapshots. Persian and English column headings are supported; UTF-8 with BOM improves compatibility with spreadsheet software.

CSV cells are serialized deterministically, and text that could be interpreted as a spreadsheet formula is prefixed with an apostrophe. Export cancellation makes no changes. The export action reports success/failure and does not modify audit data.

## Validation

Run `python -m unittest discover -s tests -q` from the project directory. The export tests cover localized headers, empty exports, snapshots, and formula-injection neutralization.

## Known limitations

The audit actor still uses the database trigger label `database-trigger`; authenticated employee attribution requires explicit propagation of the verified session identity to each reservation write. GUI execution should be checked on Windows with PySide6 installed.
