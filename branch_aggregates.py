"""Totals of the *visible*, permission-scoped cashflow comparison rows."""

def visible_totals(rows):
    """Return totals after search, advanced filtering, and sorting are applied."""
    totals = {'branches': 0, 'receipts': 0, 'expenses': 0, 'net': 0}
    for row in rows:
        totals['branches'] += 1
        for key in ('receipts', 'expenses', 'net'):
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('Financial amounts must be integer values')
            totals[key] += value
    return totals


def totals_caption(totals, language='fa', money=str):
    if language == 'fa':
        return (f"شعب قابل مشاهده: {totals['branches']}    |    دریافتی: {money(totals['receipts'])}"
                f"    |    هزینه: {money(totals['expenses'])}    |    خالص: {money(totals['net'])}")
    return (f"Visible branches: {totals['branches']}    |    Receipts: {money(totals['receipts'])}"
            f"    |    Expenses: {money(totals['expenses'])}    |    Net: {money(totals['net'])}")
