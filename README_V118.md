# Ashkan Hotel Pro v118 — monitor status and bounded retries

- Worker poll status: idle/scheduled/running/healthy/retry_wait/failed/authorization_failed/disabled.
- Nonblocking single-shot retry timer, capped at three retries with exponential delay (5/10/20 seconds).
- Authorization failures never retry automatically; fail closed.
- Admin-gated, capped security monitor failure history in SQLite; records error categories rather than sensitive exception messages.
- Monitor status and last five failure categories can be refreshed in the security analytics dialog.
- No worker overlap; UI updates occur in Qt main thread.

Run `python -m unittest discover -s tests -q`. GUI on Windows still requires manual verification.
