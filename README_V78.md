# Ashkan Hotel Pro — v78

## Reservation edit improvements
- Localized edit dialog in Persian (RTL) and English (LTR).
- Inline date validation and conflict feedback.
- Live, branch-authorized room availability check when room or dates change.
- Existing transactional server-side overlap check remains authoritative at save time.
- No database schema changes.

## Verification
`python -m unittest discover -s tests -q`: 469 tests; 459 passed and 10 skipped.
GUI testing on Windows with PySide6 remains necessary.

## Run
`python -m pip install -r requirements.txt`
`python main.py`
Back up hotel.db before upgrading.
