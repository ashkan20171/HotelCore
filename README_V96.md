# Ashkan Hotel Pro v96 — Multi-property executive dashboard

New administrator-only, bilingual dialog compares **authorized active branches** for the selected 7/30/90-day reporting window. Includes weighted occupancy, indicative ADR/RevPAR, missing-quote counts and management alerts. No guest PII. New pure analytics module `multi_property_dashboard.py` and automated tests.

**Important:** Estimates allocate stored reservation quotes and use current active inventory. They are not recognized revenue; historical room capacity is not reconstructed. A missing quote makes ADR/RevPAR unavailable. Back up `hotel.db` before upgrading. Run `py -m pip install -r requirements.txt` then `py main.py`.
