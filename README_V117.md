# Ashkan Hotel Pro — v117

## Nonblocking security monitoring

- Periodic QTimer triggers a dedicated short-lived `QThread` worker.
- Worker creates and closes its own SQLite connection and revalidates the admin session.
- Only one worker is active at a time; overlapping timer ticks are skipped.
- Signals deliver unread counts to the UI thread. No Qt widgets are touched from the worker.
- Errors stop the timer without modal dialogs and are retained as `_security_monitor_last_error` for diagnostics.
- On close, the app waits up to seven seconds for a running worker; closing is deferred if it has not finished.
- Polling is active only while the app is running. No push notifications or OS service.

Run `py -m unittest discover -s tests -q` and back up `hotel.db` before upgrading.
