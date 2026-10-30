# Ashkan Hotel Pro v65

Adds authorized monthly branch selector (all visible branches or one visible branch) and Excel export of monthly cashflow trends with a native Excel line chart. Selector options are derived from `authorized_filtered_comparison()` and `allowed_branches()`; never from all branches. Excel writer validates months, integers, and net consistency; charts are created only for nonempty rows.

Run: `py -m pip install -r requirements.txt`, then `py main.py`. Open Branch Reports, click Show Branch Trend, select a branch, and Export Monthly Trend Excel.

Back up `hotel.db` before upgrading. The cashflow chart is an Excel chart, not an in-app interactive chart. Windows GUI has not been tested in this environment.
