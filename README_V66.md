# Ashkan Hotel Pro v66

## New in v66
- Adds a responsive in-app monthly cashflow line chart rendered with PySide6 `QPainter` (no extra chart dependency).
- Plots receipts, expenses, and net cashflow and updates when the authorized branch scope/date filters change.
- Preserves the existing monthly table and Excel export.
- Validates chart data before rendering: unique `YYYY-MM` months, integer amounts, nonnegative receipts/expenses, and consistent net totals.
- Chart data is populated only from the existing authorized and filtered branch reporting path.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
```
Open Branch Reports and choose **Show Branch Trend**. The in-app chart appears above the monthly table.

## Tests
```powershell
py -m unittest tests.test_branch_trend_chart_v66 -v
```
The complete Windows GUI has not been runtime-verified in this environment. Back up `hotel.db` before replacing an existing installation. Financial trends represent recorded cashflow, not accrual-basis profit.
