# Ashkan Hotel Pro Enterprise — Stage 130

## Operational report builder

The existing administrator-only System Health dashboard now links to a bilingual operational reporting dialog with five report categories: reservations, rooms, guests, payments, and expenses. Users can select permitted columns, filter dated records by the previous 1–365 days, preview up to 250 records, and export to PDF or Excel. Undated room and guest datasets ignore the day filter.

SQL identifiers come only from static allowlists, parameters are bound, and the backend checks the actor. The UI checks the live session via `security.view` before querying and again before exporting. Guest phone numbers and national IDs are deliberately excluded. Excel cells are escaped against formula injection. Exports are created as temporary files and atomically replaced on success.

**Scope/limitations:** Export is synchronous and may block on large files. Reports are limited to 250 preview rows. Operational report presets are not yet implemented. Persian PDF requires an available Unicode font. The GUI has not been manually tested on Windows. Back up `hotel.db` before upgrading.

## Run

```bash
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -q
```
