# Stage 149 — Executive reporting UX and saved filters

- New Year-over-Year chart shows current and previous receipts, expenses, and signed cash difference (negative values supported). Uses already authorized snapshot; no new SQL queries.
- Live filtered KPI summary displays matching day count, receipts, expenses, and net difference.
- Per-actor, per-database and per-language filter presets saved via Qt QSettings. Only filter settings, not financial data, are persisted. Save overwrites the preset associated with the currently selected filter mode. Select a preset to restore it or delete it.
- Persian RTL / English LTR preserved.
- Install dependencies: `py -m pip install -r requirements.txt`; run `py main.py`.
- Automated tests are not a substitute for GUI verification on Windows.
