# Ashkan Hotel Pro v94

Room-type performance ranking by indicative RevPAR, ADR, occupancy or quoted stay value.
Includes threshold-configurable alerts and Excel-compatible UTF-8-BOM CSV export.
Controls are scoped to the currently authorized branch data already returned by `room_type_performance`.

**Limitations:** Values are reservation-quote estimates, not booked accounting revenue. Room inventory is current, not historical. The alert settings are session-only.

Run on Windows:
```powershell
py -m pip install -r requirements.txt
py main.py
```
Back up `hotel.db` before replacing any installation.
