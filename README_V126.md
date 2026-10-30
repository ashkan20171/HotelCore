# Stage 126 — Asynchronous health report exports

- System Health PDF and XLSX exports now run on a dedicated `QThread`, each with a fresh SQLite connection and a revalidated `security.view` permission.
- Progress bar displays milestone progress (5%, 25%, 85%, 100%); **not** byte-by-byte or continuous rendering progress.
- Cancel button requests cooperative cancellation. SQLite queries use a progress handler, and cancellation is checked again before publishing the report.
- Exports are written to a temporary file in the destination directory and atomically renamed on success; existing files remain intact on failure or cancellation.
- Export buttons are disabled while a report is being produced. Closing the dialog requests cancellation and waits briefly, rejecting the close if the worker cannot stop safely.
- Caveat: PDF and XLSX rendering libraries do not provide granular interruption, so cancellation may take until rendering returns. Back up `hotel.db` before upgrading. Test the graphical workflow on Windows.
