# Ashkan Hotel Pro v29 — Premium bilingual login

New login UI with an original vector SVG logo, dark navy/teal/gold theme, Persian RTL default and English LTR switch, show/hide password, Enter to sign in, inline validation, and existing PBKDF2 authentication. Language preference uses QSettings and carries into the main UI.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

## Security note
The legacy seed administrator password is intended for local evaluation only. Change it before production deployment. Authentication does not yet include rate limiting, MFA, or a password-reset flow.
