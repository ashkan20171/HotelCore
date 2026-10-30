# Stage 143 — Jalali reporting inputs and monthly exports

- Persian executive custom-date inputs use validated Jalali `YYYY/MM/DD` text and convert to Gregorian dates for SQL filtering; English keeps Gregorian Qt date pickers.
- Persian monthly table shows Jalali label for Gregorian-grouped months; tooltip retains original Gregorian month. **Grouping remains Gregorian**, not a true Jalali month rollup.
- Existing Excel/PDF exports include monthly recorded cash-flow summaries; amounts are recorded receipts/expenses, not accounting profit.
- Authorization at export time remains in place.
- Input dates limited to 90 days and today or earlier.
- UI has not been visually tested on Windows. Back up hotel.db before upgrading.
