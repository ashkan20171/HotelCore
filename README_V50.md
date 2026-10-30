# Ashkan Hotel Pro — v50

## New: bilingual management PDF export

The Branch Analytics page now includes a **Management PDF Report** button. The PDF contains selected branch, report period, recorded receipts, allocated branch expenses, net cash movement, previous-period comparison, and a monthly trend table. Persian uses RTL text shaping with `arabic-reshaper` and `python-bidi`, while English uses LTR.

**Accounting limitation:** These are recorded cash movements, not audited revenue, ADR/RevPAR, or accrual profit and loss. Historical expenses not allocated to a branch are excluded.

**Access control:** All three underlying queries enforce the selected branch authorization. PDF generation is local. No data is uploaded.

**Dependencies:** `pip install -r requirements.txt`; a Persian-capable TTF font such as Windows Tahoma or Arial must be installed. The application does not bundle fonts.

**Testing:** `python -m unittest discover -s tests -q`. Windows GUI requires manual smoke testing.

Back up `hotel.db` before upgrading.
