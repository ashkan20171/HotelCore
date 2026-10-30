# Stage 137 — Responsive Executive KPIs and stability fixes

- Responsive 1/2/3-column executive KPI grid based on window width; adapts on resize.
- Each KPI displays period-over-period percentage when mathematically defined; zero previous values are explicitly labelled as undefined (not infinity).
- Fixed missing `rooms_page` and `rooms_lay` definitions which prevented the executive dashboard dialog from opening.
- Fixed SQLite connection leaks in operational report preview and permission probe using `contextlib.closing`.
- Seven new unit tests for responsive breakpoints and period comparisons.

Run: `py -m pip install -r requirements.txt` then `py main.py`. Test: `py -m unittest discover -s tests -q`.

Note: Automated tests do not constitute a Windows GUI smoke test. Back up hotel.db before upgrade.
