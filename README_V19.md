# Ashkan Hotel Pro v19 — Security and UX hardening

Built on v18. Python / PySide6 / SQLite; Persian RTL.

## Changes
- Restrict reservation rescheduling to the active authorized branch; check source reservation and destination room on each save.
- Filter selectable rooms to the active branch.
- Scope financial CSV payment export to the active branch. Unattributed expenses are intentionally omitted until expenses carry a branch ID.
- Improve table readability, row sorting, keyboard focus outlines, navigation hit targets and accessibility labels.

## Run
`py -m pip install -r requirements.txt`
`py main.py`

## Tests
`py -m unittest discover -s tests -v`

**Limitations:** Not all legacy actions are secured; UI smoke testing on Windows is still required. Back up hotel.db before migration. Default admin credentials must be changed. This is not production ready.
