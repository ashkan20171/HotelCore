# Stage 157 — Booking coverage reporting and weekly changes

- New standalone `booking_management_v157.py`: validated and bounded booking-coverage reports, weekly comparison with percentage-point deltas, atomic Excel and PDF exports.
- The Booking Outlook tab now shows latest-week average booked coverage and week-over-week change, plus dedicated Excel and PDF export buttons.
- Exports contain **only aggregate room counts and dates**, no guest names or personally identifiable data; exports re-authorize `security.view` immediately before writing.
- Excel includes daily rows, weekly comparison and summary sheets. PDF includes daily coverage and a summary.
- These metrics compare **future recorded booking coverage**, not newly created reservations or statistically predicted demand. Partial weeks are compared as observed and may not be directly comparable.
- Persian default RTL and English LTR remain supported. GUI requires Windows manual verification.
- Tests: `python -m unittest discover -s tests -q`.
