# Stage 144 — True Jalali monthly grouping and date picker

- Persian executive monthly summaries group each daily receipt/expense by its **actual Jalali year/month** (not merely relabeling Gregorian groups). English groups by Gregorian month.
- Persian custom range now has calendar buttons with a keyboard-accessible Jalali day/month/year dialog. Inputs remain editable and are validated before queries.
- Monthly cash-flow Excel and PDF exports honor the dashboard language calendar using a `monthly_calendar` snapshot option; default remains Gregorian for API compatibility.
- Invalid/nonfinite financial values and invalid ISO dates are rejected in the new aggregator.
- Date values are still stored and queried as ISO Gregorian dates in SQLite.
- PDF Unicode rendering depends on installed fonts. This is a solar date **selector**, not a full calendar month-grid widget.
- Windows GUI needs hands-on verification. Back up hotel.db before upgrading.
