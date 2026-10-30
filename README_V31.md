# Ashkan Hotel Pro v31 — Secure account password update

- Persian RTL default; English LTR available.
- Bilingual password change dialog with current/new/confirmation inputs, show/hide toggle, inline validation.
- Password rotation service with PBKDF2-HMAC-SHA256 (240,000 iterations), random salt, constant-time comparison, and SQLite transactional update.
- Existing login throttling and hotel modules retained.
- 8 additional unit tests for password security.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Test
`py -m unittest discover -s tests -v`

Security note: local desktop credentials are not a replacement for centralized identity management. Full GUI regression testing on Windows is still required. Back up hotel.db before upgrading.
