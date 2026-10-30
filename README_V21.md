# Ashkan Hotel Pro v21 — UX and branch safety

This release extends v20 without replacing its database.

## Changes
- Table context menus and Ctrl+C copy for selected cells, with TSV formatting for Excel.
- Extended selection, accessible table descriptions, and hover styling.
- New rooms are explicitly associated with the active authorized branch.
- Branch authorization is checked before a room is inserted.

## Running
`py -m pip install -r requirements.txt`
`py main.py`

## Testing
`py -m unittest discover -s tests -v`

Back up hotel.db before upgrading. GUI interaction on Windows has not been validated. Some older application operations still need full authorization review.
