# Ashkan Hotel Pro v99 — Executive dashboard UX

Adds six premium-styled bilingual KPI tiles, filtered comparison of property ADR and RevPAR using bar indicators, and scrollable dashboard layout. All comparison data are from the existing authorized multi-property scorecard; no new database schema or personal guest data.

## Limitations
Values are **indicative booking quote allocations**, not realized revenue. Current room inventory is not historical. This release does not add a multi-page PDF report; existing PDF export is retained. UI behavior requires verification on Windows with PySide6.

## Run
`py -m pip install -r requirements.txt` then `py main.py`. Back up `hotel.db` before upgrading.
