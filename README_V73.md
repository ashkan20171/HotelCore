# Ashkan Hotel Pro v73 — Dashboard layout refresh

This release builds on v72 and focuses on dashboard presentation rather than database changes.

## Improvements
- Five dashboard KPI tiles are displayed in a two-row, three-column grid instead of a cramped five-column strip.
- KPI captions and values use separate text elements with improved typography and wrapping.
- Quick actions use a two-column grid instead of one horizontal row.
- Dashboard titles, KPI labels, chart heading, quick actions, and recent reservation headers are bilingual.
- Existing RTL/LTR shell handling and sidebar navigation grouping are preserved.
- No database schema changes.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
```

## Test
```powershell
py -m unittest discover -s tests -q
```

Visual QA of all screens at different Windows DPI settings is still needed. Back up `hotel.db` before upgrading.
