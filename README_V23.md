# Ashkan Hotel Pro — v23

## Changes
- Live, Unicode-aware search overlay in shared data tables. Press Ctrl+F to open/close; clear button restores all rows.
- Search supports Persian/Arabic letter variants, Persian/Arabic/Latin numerals, and multiple terms.
- Removed duplicate password prompt in user creation.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Tests
`py -m unittest discover -s tests -v`

## Caveats
Live search is enabled on tables created by the shared `table()` method, not every custom table. Full Windows GUI and multi-branch security integration remain unverified. Back up `hotel.db` before upgrading.
