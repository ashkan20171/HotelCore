# Ashkan Hotel Pro v71 — Navigation & bilingual UI refinement

This incremental release addresses the screenshot-reported sidebar discoverability problem.

- Adds a bilingual sidebar search that matches both Persian and English navigation names regardless of the selected UI language.
- Normalizes Persian/Arabic character variants and Unicode text to improve search usability.
- Keeps the existing RTL/LTR shell behavior and updates the sidebar search direction and placeholder when the language changes.
- Search does not query the database, alter permissions, or change existing financial records.
- Adds nine pure-Python tests for navigation search.

**Limitations:** This release is not a complete translation audit or visual redesign of all dialogs. PySide6 is not available in the build environment, so Windows GUI behavior must be validated locally. Back up `hotel.db` before upgrading.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
Test: `py -m unittest discover -s tests -q`.
