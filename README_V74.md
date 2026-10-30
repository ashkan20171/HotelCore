# Ashkan Hotel Pro v74 — Responsive dashboard

The KPI dashboard now reflows automatically from 3 columns (wide) to 2 columns (medium) or 1 column (narrow) as the available dashboard width changes. This preserves existing KPI values, role-based branch queries, and FA/EN labels. The responsive breakpoint rules are independently tested in `responsive_layout.py`, with the Qt adapter in `responsive_dashboard.py`.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Test
`py -m unittest discover -s tests -q`.

Back up `hotel.db` before updating. GUI rendering on Windows and high-DPI displays requires local verification. This release does not claim to complete all form translations or redesign all pages.
