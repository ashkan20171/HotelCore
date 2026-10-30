# Ashkan Hotel Pro Enterprise — Stage 121

## Comparative system-health analytics

- Admin-only read-only comparison of the most recent 1–90 UTC days with the immediately preceding period of equal length.
- Four indicators: number of checks, warnings, warning percentage, and maximum recorded monitor failure count.
- Configurable warning threshold (0–100%) with alerts for no recent observations, excessive warning rate, latest database warning, and latest monitor error.
- Interactive period/threshold controls in **User and role management → System health**, bilingual Persian/English.
- No background notifications or predictive analytics. Reports from Stage 120 are unchanged.
- Health results reflect recorded observations; no data is not equivalent to healthy.

## Run and test

```powershell
py -m pip install -r requirements.txt
py main.py
py -m unittest discover -s tests -q
```

Back up `hotel.db` before upgrading. Windows GUI testing remains necessary.
