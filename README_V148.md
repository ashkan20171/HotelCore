# Stage 148 — Financial filtering and filtered exports

- Bilingual advanced daily financial filters: date search, minimum, optional maximum, receipts/expenses/net/either mode.
- Filters are applied to the visible daily table without mutating the authorized snapshot.
- Optional **Export filtered days only** checkbox: Excel/PDF daily and monthly reporting is derived from filtered days. Room-type estimates remain for the full original period and must not be interpreted as filtered room revenue.
- No new SQL queries or access grants; exports retain permission reauthorization.
- Pure filtering helper and unit tests in `executive_financial_filters_v148.py`.
- Run `py -m pip install -r requirements.txt` and `py main.py`.
- GUI appearance on Windows requires manual verification.
