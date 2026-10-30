# Ashkan Hotel Pro — v22

## New in this release
- Reusable table filtering across tables built by `MainWindow.table`.
- Ctrl+F opens a filter dialog; context menu includes search and clear filter.
- Unicode normalization for Persian/Arabic characters and Persian/Arabic numerals.
- Multiple search terms must all match the row, regardless of column.
- Copying selected table cells skips filtered-out rows.
- Seven headless unit tests for search behavior.

## Running
```powershell
py -m pip install -r requirements.txt
py main.py
py -m unittest discover -s tests -v
```

## Limitations
- Filtering is added to tables constructed through `MainWindow.table`; manually created tables still require integration.
- Filtering uses a dialog rather than a persistent toolbar.
- GUI and multi-branch authorization require Windows integration and security testing before production use.
- Back up `hotel.db` before migration.
