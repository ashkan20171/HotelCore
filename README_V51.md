# Ashkan Hotel Pro v51 — Interactive cashflow chart

- Adds a custom Qt QPainter monthly receipts/expenses bar chart to Branch Analytics (navigation index 24).
- Hover each month to see receipts, expenses and net cash movement. Existing monthly table and exports remain.
- Automatically loads the chart for the initially selected branch; click Show Monthly Trend after changing dates or branch.
- Pure financial chart preparation is tested without Qt. No database migration or new dependencies.
- Figures reflect recorded payments and allocated expenses, not accounting profit or loss.
- Run `python -m unittest discover -s tests -q` and `python main.py` after installing requirements.
- On Windows, verify the GUI visually and back up hotel.db before upgrades.
