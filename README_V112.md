# Ashkan Hotel Pro Enterprise v112

- New dashboard KPI cards: successful logins, failed/locked attempts, success rate, previous-period failed attempts and delta.
- Previous-period comparison uses equal-duration UTC windows.
- Review signals based on threshold (default 5) and worsening failure count; these are heuristics, not confirmed attacks.
- Persian and English labels, dark-theme cards, multi-column arrangement.
- Back up `hotel.db` before upgrading. UI requires real Windows/PySide6 visual testing.

Run `python -m unittest discover -s tests -q` then `python main.py` after installing requirements.
