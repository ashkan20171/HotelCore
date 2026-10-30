# Stage 138 — Chart Hover & Unicode PDF

- Added mouse-hover date/value tooltips for both executive trends and booking-based occupancy.
- Added a pure, unit-tested nearest-point geometry helper.
- PDF exports now detect installed Unicode TrueType fonts and reshape Persian/Arabic labels when optional dependencies are available. Font availability is environment-dependent; no fonts are redistributed.
- Preserved previous authorization and atomic export behavior.
- **Limitations:** Qt UI not manually validated on Windows. Persian PDF fallback without an installed Unicode font may replace unsupported characters. Booking-based occupancy is not physical occupancy.
