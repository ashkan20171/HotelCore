# Ashkan Hotel Pro v111 — Interactive Security Trends

- Qt-native resizable stacked-bar chart for daily successful, failed and locked login events.
- Security dashboard includes bilingual legend, translated summary, and login success-rate KPI.
- Chart refreshes with selected time period and optional username filter.
- Pure-Python chart data aggregation with administrator-only authorization and regression tests.
- No extra charting library required. All prior application features are retained.

## Run

`py -m pip install -r requirements.txt`

`py -m unittest discover -s tests -q`

`py main.py`

Back up `hotel.db` before upgrading. GUI layout and Persian font rendering require Windows smoke testing.
