# Ashkan Hotel Pro v68 — Bilingual UI/UX and RTL/LTR refinement

## What's new
- Application-wide direction switching: Persian uses RTL; English uses LTR.
- Navigation shell mirrors with the language: sidebar on the right for Persian and on the left for English.
- Direction-aware text alignment and refreshed dark-premium visual theme with teal/blue accents, softer borders, improved spacing, tables, inputs, tabs, scrollbars and status bar.
- Expanded Persian-to-English vocabulary for common hotel workflows, reporting, finance, inventory, staff, invoices and branch management.
- Language preference remains persisted in QSettings and is applied before the main window is shown.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
```

## Tests
```powershell
py -m unittest discover -s tests -v
```
The packaged test suite completed with 412 tests passing and 10 skipped in the build environment. Python compilation checks passed. A full visual smoke test on Windows still needs to be performed because appearance can vary with installed fonts, display scaling and Qt platform plugin.

## Notes
- Persian is the default language; English can be selected from the language selector in the sidebar.
- RTL/LTR changes apply to the main window and its existing child widgets. Pages are rebuilt when switching language so controls can be translated from their canonical Persian labels.
- Data stored in SQLite is not translated or mutated by UI localization.
- Back up `hotel.db` before replacing an existing installation.
