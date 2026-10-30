"""Pure data preparation for a branch-scoped cash movement comparison chart."""
from cashflow_dashboard import cashflow_comparison

def comparison_bars(reports, language='fa', *, limit=12):
    """Return normalized bar lengths and signed net values; caller must authorize reports."""
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError('limit must be a positive integer')
    rows = cashflow_comparison(reports, language)[:limit]
    peak = max((max(row['receipts'], row['expenses'], abs(row['net'])) for row in rows), default=0)
    result = []
    for row in rows:
        result.append({**row,
            'receipt_percent': round(row['receipts'] * 100 / peak) if peak else 0,
            'expense_percent': round(row['expenses'] * 100 / peak) if peak else 0,
            'net_percent': round(abs(row['net']) * 100 / peak) if peak else 0,
            'net_negative': row['net'] < 0})
    return result
