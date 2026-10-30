# Ashkan Hotel Pro — v72

## Navigation hierarchy and bilingual UI

- Added four clearly labeled sidebar groups: Front Desk & Stays, Finance & Reports, Operations & Services, and Administration.
- Group headings switch between Persian and English with the language selector.
- Navigation search hides irrelevant group headings as well as irrelevant menu buttons.
- The 26 original navigation routes and their indices are preserved, so permissions and page navigation are unchanged.
- Kept the existing scrollable sidebar, main page layout, and SQLite schema intact.

## Run

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Test

```powershell
py -m unittest discover -s tests -q
```

**Visual verification is still needed on Windows**, especially at 125% and 150% scaling and in both RTL and LTR modes. Back up `hotel.db` before replacing an installed copy.
