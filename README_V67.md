# Ashkan Hotel Pro v67 — Multi-branch trend comparison foundation

## Added
- Added `branch_multi_trend.py`, a pure reporting helper that aligns monthly values across selected branches for side-by-side line-chart rendering.
- Supports net cashflow, receipts, and expenses as comparison metrics.
- Validates branch names, month keys, duplicate records, integer amounts, nonnegative receipts/expenses, and net consistency.
- Rejects unknown branch selections rather than silently producing incomplete comparisons.
- Missing branch/month pairs are aligned to zero so series share the same month axis.

## Important scope note
This release adds and tests the comparison-data layer. The existing v66 in-app chart remains the aggregate trend chart; a multi-line per-branch chart is not yet connected to the UI. The caller must enforce branch authorization before passing any report data to this helper.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
```

## Test
```powershell
py -m unittest tests.test_branch_multi_trend -v
```

Back up `hotel.db` before replacing an existing installation. The financial metrics represent recorded cashflow, not accrual-basis profit. The full Windows GUI has not been end-to-end validated.
