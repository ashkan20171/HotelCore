# Ashkan Hotel Pro v70 — UI stabilization

- Fixed the duplicate nested scroll areas introduced in v69. Each navigated page now has one viewport.
- Kept the shell explicitly left-to-right while positioning the sidebar on the right for Persian and left for English.
- Preserved the `navButton` selector and used the `active` property for the selected item.
- Updated version text in the status bar.
- Refined login sizing, spacing and keyboard focus, and ensured credentials are entered left-to-right regardless of language.

## Verification
Run `python -m unittest discover -s tests -q`. Visual confirmation on Windows is still required.

## Running
`py -m pip install -r requirements.txt` then `py main.py`.

Back up your existing `hotel.db` before replacing your installation.
