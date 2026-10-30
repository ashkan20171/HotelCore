# Ashkan Hotel Pro v42 — Native Excel reporting

Branch Reports now supports **Excel Workbook (.xlsx)** and CSV. The native workbook includes RTL/LTR sheet direction, a bilingual header, a branch/date subtitle, styled alternating rows, frozen headers, and autofilters. Exported values are treated as text and spreadsheet-formula prefixes are escaped. Existing per-branch access checks and SQLite schema are unchanged.

Install: `py -m pip install -r requirements.txt`
Run: `py main.py`
Tests: `py -m unittest discover -s tests -v`

Back up `hotel.db` before upgrading. GUI operation on Windows has not been verified in this environment.
