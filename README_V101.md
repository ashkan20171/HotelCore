# Ashkan Hotel Pro v101 — secure first-run setup

## New features
- First-run administrator setup wizard in Persian (RTL) and English (LTR).
- No hard-coded `admin / Admin@123456` account for fresh installations.
- Password confirmation, strength requirements, salted PBKDF2-SHA256 (240,000 rounds) compatible with existing authentication.
- A first-run wizard is shown only if the `users` table is empty.
- Existing accounts are preserved; no password is reset automatically.
- Regression tests for first-run setup and account creation.

## Start
```powershell
py -m pip install -r requirements.txt
py main.py
```

For a new database, enter a username and a strong unique password when prompted. For an existing `hotel.db`, use your existing credentials.

## Security limitations
This update improves fresh-install credential handling, but is not a full authentication or authorization audit. Existing weak accounts should have their passwords changed. Do not publish `hotel.db` to GitHub. Run Windows UI QA before production.
