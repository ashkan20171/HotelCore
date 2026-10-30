# Stage 142 — Custom reporting dates and monthly rollups

- Date-range selection (up to 90 days; future dates disallowed), while retaining the 1–90 day quick selector.
- The executive snapshot accepts `start_date` and `end_date` as optional inclusive `datetime.date` objects, with an equal-length previous period.
- A fourth tab summarizes monthly recorded receipts, expenses and their difference, calculated from the authorized daily snapshot.
- No claims of recognized revenue, profit or physical occupancy.
- Existing RBAC and export reauthorization are retained.
- Date pickers use Gregorian ISO dates in both languages; Jalali calendar controls are not implemented.
- The UI has not been manually tested on Windows.
