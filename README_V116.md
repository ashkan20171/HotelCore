# Ashkan Hotel Pro — v116

## Periodic security monitoring

- Active administrators may enable/disable periodic checks and choose 1–60 minutes.
- Default: enabled, every five minutes. Settings stored in SQLite and migrated automatically.
- Uses a PySide6 QTimer on the UI thread; no network calls, background worker or push notifications.
- Polls the global seven-day login activity window, records actionable alert snapshots, and syncs the notification inbox.
- Existing deduplication prevents duplicate alert snapshots and inbox records for unchanged states.
- Updates the sidebar unread count; does not open intrusive dialogs.
- Authorization is rechecked every tick. Timer stops on permission/session/database failure.
- A poll is executed at the configured interval, not immediately on login. Dashboard still offers manual refresh.

**Important:** QTimer executes synchronously on the UI thread; very large databases could momentarily delay the interface. Real-time monitoring and OS notifications are not implemented.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
Test: `py -m unittest discover -s tests -q`.
Backup `hotel.db` before upgrading.
