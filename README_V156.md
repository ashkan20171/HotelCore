# Stage 156 — Booking coverage calendar and operational insights

- Seven-column calendar of recorded future booking coverage, Persian Saturday-first and English Monday-first.
- Low (amber), moderate (teal), high (green) and unavailable (gray) occupancy categories; high is 80% or above.
- Day-specific booking coverage and room count in hover details.
- Operational summary: count of low/moderate/high coverage days and longest consecutive low-coverage streak.
- Threshold for low coverage and horizon continue to use the existing controls (7–90 days).
- **Not a statistical demand forecast**; data derives from confirmed recorded reservations.
- Calendar dates remain Gregorian internally; Persian mode displays Jalali labels.
- Run: `python -m unittest discover -s tests -q`.
- PySide6 Windows GUI still requires manual verification.
