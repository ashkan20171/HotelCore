# Ashkan Hotel Pro — v30

## New in v30
- Brand SVG displayed in the main application sidebar as well as the login dialog.
- Persistent per-username login throttling: 5 failed attempts lock sign-in for 15 minutes.
- PBKDF2 check also runs for unknown usernames to reduce timing-based enumeration.
- Successful authentication clears failed-attempt counters.
- SQLite migration creates `login_attempts` automatically.
- Seven new automated tests.

## Limitations and security notes
- This is a local SQLite-based desktop application, not a centralized identity service. Lockout is per username, not per device/IP. Database write access can bypass the mechanism.
- Password reset is not yet implemented; do not implement unauthenticated reset using only username.
- Existing seeded admin password is for development only and must be changed before production.
- Persian remains default; English is selectable. Some screens remain partially translated.
- Full Windows GUI testing has not been performed.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
py -m unittest discover -s tests -v
```
Back up `hotel.db` before upgrading.
