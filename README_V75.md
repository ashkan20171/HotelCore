# Ashkan Hotel Pro — Version 75

- Booking form: improved RTL/LTR direction, field dimensions, localized placeholders, phone/national-ID LTR editing.
- Both check-in and check-out fields now show invalid state when the date range fails validation.
- Pure booking validation now rejects malformed phone characters, invalid room identifiers, and excessively long guest names.
- Added regression tests in `tests/test_booking_validation_v75.py`.

Run: `python -m unittest discover -s tests` then `python main.py`.

Back up `hotel.db` before upgrading. Qt GUI has not been visually verified on Windows.
