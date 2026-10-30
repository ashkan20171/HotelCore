# Ashkan Hotel Pro — v24

## Updates
- Booking form shows inline Persian validation messages for guest name, phone, room and stay dates.
- Persian/Arabic digits are accepted in phone validation.
- Added independent `reservation_validation.py` and six unit tests.
- Improved table live-search focus and booking form spacing.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

## Tests
`py -m unittest discover -s tests -v`

## Important
Back up `hotel.db` before upgrading. No schema migration is required for this release. The Qt GUI has not been verified on Windows; access control across legacy screens still requires a full security audit.
