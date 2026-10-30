# Ashkan Hotel Pro Enterprise — Stage 122

## Interactive daily system-health trends

- Admin-only, UTC-bounded daily aggregation for the selected 1–90 day period.
- Responsive native Qt chart with hover tooltips, warning-rate bars, threshold guide and status colors.
- Empty dates are rendered as no observations (not falsely marked healthy).
- Period and threshold controls refresh both the comparison table and the trend chart.
- Persian/English chart legends; source records are not modified by the chart.

Run: `py -m pip install -r requirements.txt`, then `py main.py`.
Test: `py -m unittest discover -s tests -q`.
Back up `hotel.db` before upgrading. Windows GUI integration still needs manual verification.
