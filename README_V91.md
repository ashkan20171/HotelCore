# Ashkan Hotel Pro — v91

## Room-type accommodation analytics

- Room-type breakdown inside the existing Revenue & Occupancy dashboard (Persian/English).
- Current active inventory, occupied room-nights, occupancy percentage, indicative accommodation value, ADR, RevPAR and missing quotes.
- Branch authorization, current-room type attribution, half-open date windows and partial quote allocation.
- Actionable alerts for missing quotes, calculated overcapacity and low occupancy.
- New isolated unit tests: `tests/test_room_type_analytics_v91.py`.

**Limitations:** These are indicative accommodation booking values, **not recognized or collected revenue**. Quotes are spread evenly across booked nights; room types reflect current room assignments, and capacity uses current active inventory rather than historical snapshots. Missing quotes suppress ADR and RevPAR. This release does not add historical transfer-aware room-type attribution or new accounting integration.

To run: `py -m pip install -r requirements.txt` then `py main.py`. Back up your existing `hotel.db` before replacing files; the archive does not include the database.
