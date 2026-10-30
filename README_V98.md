# Ashkan Hotel Pro v98

- Multi-property dashboard: compare current occupancy to a preceding equal-length window, with authorization checks on both periods.
- PDF reports in English or Persian, with RTL text shaping and an embedded Unicode font for Persian.
- Existing search, alerts, charts and PDF export remain available.
- PDF values are **indicative reservation quote allocations, not recognized revenue**. Inventory is current rather than historical.
- Persian PDF requires `arabic-reshaper`, `python-bidi` and a suitable installed TTF (Windows Tahoma or Noto Sans Arabic).

Run `py -m pip install -r requirements.txt` and `py main.py`. Back up `hotel.db` first.
