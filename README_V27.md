# Ashkan Hotel Pro v27 — Persian/English UI

- Persian (`fa`) is the default; select **English** from the language picker in the sidebar.
- Direction switches from RTL to LTR and back without restarting.
- Navigation and shared UI labels, buttons, placeholders, combo choices and table headings are translated where dictionary entries exist.
- Booking form labels also support English.
- Business values stored in SQLite remain unchanged, including statuses and payment methods.
- **Known limitation:** This is an initial localization pass. Some module-specific text, modal dialogs, reports and exported PDFs remain Persian.
- Tests: `py -m unittest discover -s tests -v`.
- Run: `py -m pip install -r requirements.txt` then `py main.py`.
