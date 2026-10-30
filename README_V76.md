# Ashkan Hotel Pro v76

## Changes
- Guest list: instant search across name, phone and national ID; Persian/Arabic digits and letter variants supported.
- Payments: inline bilingual validation feedback and invalid-field highlights without interruptive popups.
- Status bar version updated to v76.
- Added `guest_search.py` and five unit tests.

## Verification
`python -m unittest discover -s tests -q`: 453 tests (443 passed, 10 skipped).
Syntax and ZIP archive checks performed. PySide6 desktop rendering on Windows has not been verified.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

Back up your existing hotel.db before upgrading.
