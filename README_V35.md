# Ashkan Hotel Pro v35

## Implemented
- Bilingual invoice preview with Persian RTL and English LTR layouts.
- HTML escaping of invoice field values to prevent HTML injection.
- English invoice dialog heading and adjustment action.
- Version display refreshed.
- Five unit tests for invoice presentation.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Tests
`py -m unittest discover -s tests -v`

## Limitations
- Invoice PDF export and some legacy dialogs remain Persian.
- Windows graphical end-to-end test not performed.
- Back up `hotel.db` before moving it to the new folder.
