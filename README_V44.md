# Ashkan Hotel Pro v44 — Branch Comparison

Added authorized multi-branch Excel comparison to Branch Reports. Includes occupancy %, recorded collections, occupied and available room-nights, a chart and bilingual RTL/LTR headings. Data is limited to branches allowed for the signed-in user.

**Financial caveat:** Collected per occupied room-night is not ADR or RevPAR. Accurate ADR/RevPAR needs recognized room revenue and an explicit accounting policy. The available room-night denominator is based on currently active rooms, not historical room availability; treat historical occupancy as an estimate.

Run: `py -m pip install -r requirements.txt` then `py main.py`. Test: `py -m unittest discover -s tests -v`. Back up hotel.db before upgrading.
