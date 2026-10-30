"""Validated per-branch monthly trend series for comparison charts.

The caller must pass only branch reports already authorized for the current user.
Missing branch/month combinations are represented as zero, because no cashflow
records were returned for that branch and month within the selected reporting range.
"""
from datetime import date

_METRICS = ('receipts', 'expenses', 'net')


def build_branch_trend_series(branch_reports, selected_branches=None, metric='net'):
    """Return ``{'months': [...], 'series': [{'branch': ..., 'values': [...]}]}``.

    ``branch_reports`` is an iterable of ``(branch_name, rows)`` where each row
    has month (YYYY-MM), receipts, expenses and net. If selected_branches is
    supplied, only those exact branch names are included. Unknown selections
    raise ValueError instead of silently returning an incomplete chart.
    """
    if metric not in _METRICS:
        raise ValueError('Unsupported metric')
    reports = {}
    all_months = set()
    for name, rows in branch_reports:
        if not isinstance(name, str) or not name.strip() or name in reports:
            raise ValueError('Invalid or duplicate branch')
        normalized = {}
        for row in rows:
            month = row.get('month')
            try:
                parsed = date.fromisoformat(month + '-01') if isinstance(month, str) else None
            except ValueError as exc:
                raise ValueError('Invalid month') from exc
            if parsed is None or parsed.strftime('%Y-%m') != month or month in normalized:
                raise ValueError('Invalid or duplicate month')
            values = [row.get(key) for key in _METRICS]
            if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
                raise ValueError('Financial values must be integers')
            receipts, expenses, net = values
            if receipts < 0 or expenses < 0 or net != receipts - expenses:
                raise ValueError('Inconsistent cashflow')
            normalized[month] = dict(zip(_METRICS, values))
            all_months.add(month)
        reports[name] = normalized

    if selected_branches is None:
        selected = sorted(reports)
    else:
        selected = list(dict.fromkeys(selected_branches))
        if any(name not in reports for name in selected):
            raise ValueError('Unknown selected branch')
    months = sorted(all_months)
    series = []
    for name in selected:
        values = [reports[name].get(month, {}).get(metric, 0) for month in months]
        series.append({'branch': name, 'values': values})
    return {'months': months, 'metric': metric, 'series': series}
