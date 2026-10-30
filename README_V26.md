# Ashkan Hotel Pro v26

## New
- Atomic SQLite reservation creation with `BEGIN IMMEDIATE` and rollback on failure.
- Room branch authorization, overlapping reservation prevention, and pricing snapshot inside one transaction.
- Five integration-style tests using in-memory SQLite.
- Persian inline validation feedback and invalid-field visual styling.

## Run
`py -m pip install -r requirements.txt`
`py main.py`
`py -m unittest discover -s tests -v`

**Important:** Back up `hotel.db` before upgrading. GUI execution on Windows and all legacy authorization paths remain unverified. SQLite is intended for local deployment, not concurrent multi-server use.
