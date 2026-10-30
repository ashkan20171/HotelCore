# Stage 146 — Like-for-like year-over-year financial comparison

- The executive dashboard now shows a year-over-year comparison of **recorded receipts, expenses and their difference**.
- The comparison window has exactly the same number of days and begins on the corresponding Gregorian date in the prior year. Feb 29 maps to Feb 28 in non-leap years.
- Includes amount and percentage changes, with an em dash for undefined percentages where the prior period is zero.
- Uses bounded, parameterized, read-only SQL queries in the existing authorized worker; no additional UI-thread database access.
- The comparison is **Gregorian-year based even in Persian UI**; it is not a Jalali-year comparison or an annual profit statement.
- Default Persian RTL / optional English LTR remain unchanged.
- Run `py -m pip install -r requirements.txt` then `py main.py` on Windows.
- PySide6 GUI needs manual verification on Windows.
