# Stage 125 — Background overview and cooperative cancellation

- Overview, history, and summary metrics now load via an authorized background QThread with its own SQLite connection.
- Dashboard analytics and overview workers use SQLite progress handlers and thread-safe cancellation events.
- Refresh is coalesced while the overview worker runs; status messages and refresh-button state track progress.
- Closing or rejecting the dashboard requests cancellation and waits briefly for worker cleanup.
- PDF/Excel export remains synchronous; it is not yet covered by the cancellation mechanism.
- Back up hotel.db before upgrading. GUI interaction requires validation on Windows.
