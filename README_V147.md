# Stage 147 — Jalali-aware year-over-year executive reporting

- Persian dashboard compares equal-length windows starting on the corresponding date of the **previous Jalali year**; English uses Gregorian years.
- Leap-day fallback: Esfand 30 maps to Esfand 29 if the previous Jalali year is not leap.
- Bounded, authorized read-only queries remain in the dashboard worker.
- Daily activity table adds a **minimum receipt-or-expense amount** filter. This is a view-only filter; exports still cover the entire authorized date window.
- Both Persian RTL and English LTR remain available.
- Install requirements (`jdatetime` is needed for Persian calendar features), then run `py main.py`.
- Manual Windows GUI verification is still required.
