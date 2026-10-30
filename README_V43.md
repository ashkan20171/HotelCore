# Ashkan Hotel Pro v43 — Executive Excel Reporting

The Branch Reports page now includes **Executive Excel Report** alongside the original CSV/XLSX reservation export. The new workbook contains four sheets: Executive Summary, Reservations, Payments and Revenue Trend, including a monthly bar chart when payments exist. All content is branch-scoped and authorized before export; payment dates use the report interval `[start, end)` and totals represent recorded payments, not earned revenue. User-entered text is safely escaped to prevent spreadsheet formula injection. The report is bilingual (FA RTL / EN LTR), with money in Toman. No SQLite schema changes.

Run `py -m pip install -r requirements.txt`, then `py main.py`. Tests: `py -m unittest discover -s tests -v`. Back up `hotel.db` before upgrading. GUI execution on Windows has not been verified here.
