# Ashkan Hotel Pro v84

Room transfer history now supports optional localized date inputs (Jalali for Persian, Gregorian for English), date validation, and PDF export. Existing calendar filters remain available; entered dates override calendar dates. PDFs currently use English column headers for legibility; full Persian PDF typography is pending. Database schema is unchanged.

Run: `python -m pip install -r requirements.txt` then `python main.py`.
Tests: `python -m unittest discover -s tests`.
