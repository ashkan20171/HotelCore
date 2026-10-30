# Stage 140 — Dashboard data browsing and connection lifecycle

- Added an explicit SQLite connection context manager that closes on both success and failure (unlike sqlite3.Connection context manager, which commits/rolls back but does not close).
- Executive dashboard worker and export reauthorization use this manager; exports use read-only SQLite mode.
- Room-type table supports case-insensitive search and sortable columns.
- Daily cash-flow table supports sorting with numeric values and correct detail lookup by selected date after sorting.
- Table sorting is suspended during population to prevent mismatched rows.
- Automated connection-lifecycle tests. Persian RTL and English LTR retained.

Run: `python -m unittest discover -s tests -q`.

Caveats: dashboard aggregates are limited to 90 days; some legacy DB connections elsewhere remain to be audited. GUI appearance needs manual Windows validation. Booked room value is not recognized revenue.
