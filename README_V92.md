# Ashkan Hotel Pro v92

Adds room-type comparison for two equal-length periods to the Revenue & Occupancy Dashboard. Occupancy percentage-point change, estimated ADR change, and estimated RevPAR change are calculated per room type. Comparisons are restricted to the active authorized branch. Missing booking quotes produce unavailable estimates rather than misleading values.

**Important:** These are indicative booking-quote metrics, not recognized revenue. Current inventory and room types are used for historical periods. Back up hotel.db before upgrading.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
