# Stage 128 — Report presets and Windows packaging starter

- Admin-specific, SQLite-persisted named presets for health analysis **days** and **warning threshold**.
- Save, apply and delete from System Health dialog. Max 20 presets per admin, validated input and authorization.
- New tests for validation, isolation, authorization, updates and limits.
- `build_windows.ps1` is a **starter script** for PyInstaller on Windows, not a pre-built installer. PyInstaller may need additional hooks/assets for production.
- The existing PDF/Excel export formats are unchanged; these presets configure health analysis filters, not report content templates.
- Test the GUI and packaged output on Windows before distribution. Back up hotel.db first.
