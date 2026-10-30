# Ashkan Hotel Pro v36 — Bilingual PDF invoices

- Added `invoice_pdf.py` with Persian RTL and English LTR invoice PDF generation.
- Persian text uses Arabic shaping and bidi; English text is written directly.
- Uses the active user's language and existing locale date/money formatting.
- Branch authorization remains checked before invoice generation.
- Uses installed TrueType fonts (no redistribution of system fonts).
- Includes six unit tests for labels, validation, font detection and PDF output.

## Run
`py -m pip install -r requirements.txt`

`py main.py`

## Tests
`py -m unittest discover -s tests -v`

## Known limitations
- Windows GUI end-to-end testing not performed.
- Some legacy dialogs remain untranslated.
- English money still uses toman, without currency conversion.
- Back up hotel.db before transferring between versions.
