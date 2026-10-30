# Stage 150 — Interactive financial charts and responsive sizing

- Added pointer hover details for monthly cashflow bars, in Persian and English. Shows recorded receipts, expenses and cash difference, including negative values.
- Added pointer hover details for current vs prior-year chart, in both languages.
- Added pure, unit-tested chart hit-testing, tooltip localization and responsive chart-height helpers.
- Adjusted minimum chart heights for narrow/wide dashboard windows without introducing third-party chart dependencies.
- **Scope:** this stage does not introduce a new historical multi-year query or claim multi-year comparisons. Existing YoY comparison remains intact.
- Run: `py -m pip install -r requirements.txt` then `py main.py`.
- GUI behavior still needs manual validation on Windows with Qt installed.
