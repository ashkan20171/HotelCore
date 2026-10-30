# Ashkan Hotel Pro — v85

## Persian/English Room Transfer PDF

- Fully localized Persian and English report labels and summary.
- Embeds an installed Unicode TTF (Tahoma on Windows; Noto/DejaVu on Linux). No font is distributed.
- Persian shaping through `arabic-reshaper` and `python-bidi`.
- Right-to-left table column ordering in Persian mode.
- Repeating table header, page breaks, long text wrapping, and HTML escaping.
- Source data is already filtered to authorized branch in the GUI.

Run: `py -m pip install -r requirements.txt` then `py main.py`.
Test: `py -m unittest discover -s tests`.

Backup hotel.db before replacing your prior installation.
