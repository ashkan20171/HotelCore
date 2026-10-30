# Ashkan Hotel Pro v54 — Visual Branch Comparison

Adds a bilingual visual comparison of branch receipts, expenses and net cash movement to Branch Analytics. Uses existing branch authorization and the selected date interval. Bars are normalized to a common scale; negative net movements appear in coral. This is cash movement, **not** accrual profit.

## Run
`python -m pip install -r requirements.txt` then `python main.py`. Open Branch Analytics and click Compare Branch Cash Movement.

## Verify
`python -m unittest discover -s tests -q`

Back up `hotel.db` before replacing a prior installation. GUI smoke testing on Windows is recommended.
