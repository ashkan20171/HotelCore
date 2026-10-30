# Ashkan Hotel Pro — v20

## New in v20
- Branch-scoped dashboard: occupancy, active rooms, pending bookings, payments, monthly revenue and latest reservations.
- Quick-action buttons to reservations, occupancy planner, payments and branch reports.
- Improved KPI hierarchy and dashboard visual polish.
- Pure dashboard_metrics.py calculations with dedicated tests.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

## Tests
`py -m unittest discover -s tests -v`

## Migration
Back up hotel.db before copying it from v19. Do not copy a production database without testing the migration on a backup.

## Limitations
GUI was not validated on Windows. This is a development build; older authorization paths require further review. Financial KPIs represent recorded payments, not accrued revenue.
