# Stage 124 — Asynchronous Health Dashboard

- Background QThread fetch for comparative health analytics with a dedicated SQLite connection.
- Live session/permission validation on the worker connection.
- Debounced (250ms) filter changes, one worker at a time, stale result suppression.
- Loading/queued/error states, disabled manual refresh while busy, safe close waiting.
- Fixed missing `security.view` mapping in `operation_guard.ACTION_PERMISSIONS` that blocked security dashboard actions.
- GUI must be tested on Windows with PySide6 installed. Back up `hotel.db` before upgrading.
