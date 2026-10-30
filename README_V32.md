# Ashkan Hotel Pro — v32

## Improvements
- Shared `locale_format.py` for Persian Jalali and English Gregorian display dates.
- Persian and English amount labels: **toman** remains the currency in both languages (no ungrounded FX conversion).
- Main window data tables, occupancy map, dashboard cards, and invoice view now use the active language for dates and amounts.
- ISO Gregorian values remain unchanged in SQLite, ensuring date comparisons and queries still work.
- Seven additional unit tests for locale formatting.

## Limitations
- Some legacy labels, PDF exports and modal dialogs remain Persian and need dedicated translation.
- Windows GUI smoke testing has not been completed.

## Run
`py -m pip install -r requirements.txt`
`py main.py`
`py -m unittest discover -s tests -v`

Back up `hotel.db` before upgrading.
