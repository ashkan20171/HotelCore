# Architecture overview

- **Presentation:** PySide6 (`main.py`, specialized Qt widgets, RTL/LTR localization).
- **Persistence:** SQLite (`hotel.db`, schema migrations and branch-scoped query modules).
- **Business rules:** reservation, occupancy, branch authorization, pricing, cash flow and performance modules.
- **Reporting:** CSV, Excel, PDF and chart presentation modules.
- **Operations:** `enterprise_maintenance.py` and headless `enterprise_cli.py`.

## Boundaries
Each business operation must verify authorized branch access before querying or mutating data. Dashboard values are indicative quote allocations, not ledger-recognized revenue. GUI is desktop-local, not a hosted multi-tenant API.

## Modernization roadmap
1. Separate the large `main.py` into views, controllers and application services.
2. Centralize localization keys and test all Persian/English dialogs.
3. Replace fresh-install default credentials with a secure first-run setup.
4. Introduce reproducible Windows packaging, dependency locking and CI.
5. Add recovery drills, audit retention and structured error reporting.
