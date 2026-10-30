# Ashkan Hotel Pro v33

- Expanded bilingual UI vocabulary for booking and account dialogs.
- Booking validation errors now pass through the language translator (Persian default, English switch).
- Added `translation_audit.py` to detect missing exact-match translations and report coverage.
- Five additional unit tests.
- Original database values remain unchanged.

**Limitations:** Not all legacy dialog messages or PDF reports are translated. No Windows GUI end-to-end smoke test performed.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
Tests: `py -m unittest discover -s tests -v`.
Back up hotel.db before migration.
