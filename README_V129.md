# Stage 129 — Custom Health Report Builder

Admin-only custom health report builder, opened from **System Health → Custom Report Builder**.

- Choose and reorder? **Choose** up to four supported columns (fixed source order), days (1–365), and healthy/warning/all filter.
- Preview up to 250 recent matching records (UTC); read-only query with parameterized bounds.
- Save, apply, and delete up to 20 named templates **per administrator** in SQLite.
- Export the current preview to Excel or PDF with temporary-file replacement; Excel escapes formula-like cells.
- Bilingual FA/EN interface; Persian PDF requires a local Unicode font and optional Arabic shaping libraries.
- Export is synchronous in this stage; large reports may briefly block the modal (250-row preview cap).
- No automatic report scheduling or arbitrary SQL. Test on Windows and back up hotel.db before upgrading.
