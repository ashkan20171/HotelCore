# Ashkan Hotel Pro Enterprise — v100

**Milestone:** enterprise maintenance, safe backup, automated integrity checks, and recruiter-ready repository hygiene.

## New in v100
- `enterprise_maintenance.py`: SQLite read-only integrity checks, foreign-key checks and required-table checks. No personal records in health output.
- `enterprise_cli.py`: headless `health` and `backup` subcommands (no PySide6 required).
- Consistent backup via SQLite backup API, with exclusive target creation, validation and cleanup on failure.
- `.gitignore` protects live hotel databases, backup files, environment secrets, caches and local build artifacts.
- Automated regression tests for backup, integrity, missing schema and CLI.
- `ARCHITECTURE.md`, `SECURITY.md` and `RELEASE_CHECKLIST.md`.

## Installation (Windows 11)
```powershell
py -m pip install -r requirements.txt
py main.py
```

## Maintenance
```powershell
py enterprise_cli.py health
mkdir backups
py enterprise_cli.py backup --output-dir backups
py -m unittest discover -s tests -q
```
Use the backup command while the app is running if needed: SQLite backup API creates a consistent snapshot.

## Important
- **Do not upload `hotel.db` or backup files to GitHub.**
- Initial installation credentials and legacy authentication flows require a security review before public deployment.
- The new maintenance CLI does not replace offsite encrypted backups, access controls or a disaster-recovery plan.
- Revenue metrics remain indicative booking quotes, not recognized accounting revenue.
- UI visual QA and Windows integration testing are still required.
