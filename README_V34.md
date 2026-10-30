# Ashkan Hotel Pro v34

- Extended bilingual Persian/English labels in the add-room workflow.
- Room type selection is localized for display, then mapped to canonical Persian database values to preserve compatibility.
- Localized payment validation messages and common workflow labels.
- Added `localize_errors()` helper and eight unit tests.

Run `py -m pip install -r requirements.txt` and `py main.py`.
Tests: `py -m unittest discover -s tests -v`.

Limitations: Other legacy dialogs and PDF exports still contain Persian text; Windows GUI end-to-end test not performed. Back up hotel.db before migrating.
