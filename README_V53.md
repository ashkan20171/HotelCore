# Ashkan Hotel Pro — v53

## Finance KPI cards / کارت‌های شاخص مالی

- Three styled bilingual cards for recorded receipts, branch expenses and net cash movement.
- Current value and period-over-period percentage with visual directional indicators.
- Financial indicators are **cash movements**, not accrual profit.
- The previous period has the same number of days as the selected period.
- Values are queried through existing branch-authorized services; no extra database permissions or schema changes.
- Persian RTL and English LTR labels. Cards include accessible names.
- Automatically loads on opening Branch Analytics and refreshes on the comparison action.

## Run
`py -m pip install -r requirements.txt` then `py main.py`.

## Tests
`py -m unittest discover -s tests -q`.

Back up `hotel.db` before upgrading. GUI integration requires testing on Windows.
