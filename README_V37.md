# Ashkan Hotel Pro v37 — Bilingual guests and payments

- Guests page: localized heading, table labels, guest count and accessibility name.
- Payments page: bilingual field labels, button, reservation selector and transaction table.
- Payment methods use localized display labels but persist the original canonical Persian values in SQLite.
- All queries remain restricted to the active authorized branch.
- Default language is Persian (RTL); English (LTR) can be selected from the sidebar.
- Run: `py -m pip install -r requirements.txt` then `py main.py`.
- Tests: `py -m unittest discover -s tests -v`.
- Limitations: legacy dialogs and full GUI Windows end-to-end behavior still require testing.
