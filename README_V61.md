# Ashkan Hotel Pro v61 — Branch Period Insights

- Compare net cash movement of the **currently visible, authorized branches** against the immediately preceding equal-length period.
- Show current net, prior net, signed change and percent change (undefined for zero baseline).
- Highlight improvements and declines and summarize negative-net branches.
- Persian RTL and English LTR labels.
- The comparison is cash movement, **not** accrual accounting profit.

Open **Branch Analytics / گزارش شعب**, apply filters, then click **Compare Branch Periods / تحلیل تغییرات شعب** or the main branch comparison button.

Before updating, back up `hotel.db`. Install dependencies using `pip install -r requirements.txt`, then `python main.py`.

Run `python -m unittest discover -s tests -q` and `python -m compileall -q .`.
