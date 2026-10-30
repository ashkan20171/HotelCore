# Ashkan Hotel Pro v108 — Permission Audit Trail

## New in v108
- Dedicated `permission_audit` history stores actor, target, permission key, previous value, new value and timestamp.
- Permission changes record the old and new values (`default`, `allow`, `deny`) before the change is presented as complete.
- Admin-only UI to inspect the selected user's permission history and export a CSV.
- CSV export uses UTF-8 BOM for Excel and neutralizes formula-like cells.
- Permission history is scoped to the selected account; the service verifies active administrator access.
- Existing `security_events` records remain compatible.

## Run
```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -q
py main.py
```

Back up `hotel.db` before upgrading. UI has not yet been verified on Windows. This release is a portfolio-stage desktop build, not a certified production PMS.
