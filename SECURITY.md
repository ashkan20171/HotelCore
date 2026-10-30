# Security notes

- Never commit the operational database, SQLite WAL/SHM files, credentials or backups.
- Before production use, **change the bootstrap admin password** and review default-account provisioning in `main.py`.
- Restrict OS permissions on `hotel.db` and `backups/`; store encrypted copies off-device.
- Check `py enterprise_cli.py health` after upgrades and periodically test restoring a backup to a separate machine.
- Authorization must be enforced by data-access functions, not just hidden buttons.
- Exported reports may contain commercially sensitive data. Share only with authorized staff.
- This is a portfolio-stage desktop application, not a certified production hotel PMS.
