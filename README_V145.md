# Stage 145 — Jalali month-grid and monthly comparison chart

- Replaces the previous year/month/day selector with a **Saturday-first, seven-column Jalali calendar grid**.
- Supports previous/next month, year/month selectors, Today, cancellation, and keyboard-accessible day buttons.
- Invalid Esfand 30 is omitted in non-leap Jalali years; selection still uses the existing validated Jalali-to-Gregorian converter.
- Adds a receipts-vs-expenses **monthly bar chart** above the monthly table in the executive dashboard, based on actual Jalali months for Persian UI and Gregorian months for English UI.
- Financial data is recorded cash flow, **not** accounting profit or recognized revenue.
- Python unittest and syntax checks are available; GUI requires hands-on verification on Windows with PySide6 and jdatetime installed.

## Run

```powershell
py -m pip install -r requirements.txt
py main.py
```
