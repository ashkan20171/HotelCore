# Ashkan Hotel Pro — v39

Added a modal Jalali date picker to both check-in and check-out fields in the booking dialog. The picker converts selected Persian dates to Gregorian ISO-8601 for existing SQLite storage, handles leap-year Esfand and does not change persisted schema. The English UI still offers the Jalali picker as an optional calendar.

## Run
`py -m pip install -r requirements.txt`
`py main.py`
`py -m unittest discover -s tests -v`

Before upgrading, back up your existing `hotel.db`. Full Windows GUI smoke tests have not been performed.
