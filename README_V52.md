# Ashkan Hotel Pro — v52

## Jalali date filters for branch reporting

- Persian users can choose start/end dates with the native Jalali modal on the Branch Analytics screen.
- Gregorian ISO dates remain the internal representation for database queries, exports, and charts.
- The existing QDateEdit widgets remain available for keyboard/date entry.
- English mode retains the original Gregorian date inputs.
- Choosing Cancel does not modify the selected date.
- Existing role and branch access checks remain unchanged.

## Run

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Tests

```powershell
py -m unittest discover -s tests -q
```

Back up hotel.db before updating. GUI validation on Windows is still recommended.
