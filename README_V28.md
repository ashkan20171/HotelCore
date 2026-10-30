# Ashkan Hotel Pro v28 — Persistent bilingual UI

- Persian remains the first-run default; English is selectable from the sidebar.
- The selected language is saved using `QSettings('AshkanHotelPro', 'HotelPMS')` and restored on next launch.
- Switching applies RTL/LTR without restarting and regenerates navigation and common page controls.
- Translation is reversible, using original Persian UI text and table-header metadata, so EN→FA does not leave translated headers behind.
- The current page is translated after it is rebuilt (including content inside its scroll area).
- More English labels were added. Persisted business values, reservation statuses and table data are not rewritten.
- Remaining limitations: Some dialogs, PDF reports, user-facing errors and date/currency formats are still Persian-specific. Full Windows GUI testing is required.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
Tests: `py -m unittest discover -s tests -v`.
