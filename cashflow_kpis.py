"""Authorized period-over-period cash movement comparisons (exclusive end dates)."""
from datetime import date, timedelta
from branch_cashflow import cashflow

def comparison_period(start, end):
    begin, finish = date.fromisoformat(start), date.fromisoformat(end)
    if begin >= finish:
        raise ValueError('Invalid date range')
    duration = finish - begin
    return (begin - duration).isoformat(), begin.isoformat()

def percentage_change(current, previous):
    if previous == 0:
        return None if current else 0.0
    return round((current - previous) * 100.0 / abs(previous), 1)

def compare_cashflow(conn, *, branch_id, user_id, role, start, end):
    previous_start, previous_end = comparison_period(start, end)
    current = cashflow(conn, branch_id=branch_id, user_id=user_id, role=role, start=start, end=end)
    previous = cashflow(conn, branch_id=branch_id, user_id=user_id, role=role, start=previous_start, end=previous_end)
    keys = ('receipts', 'expenses', 'net_cash_movement')
    return {
        'current': {key: int(current[key]) for key in keys},
        'previous': {key: int(previous[key]) for key in keys},
        'changes': {key: percentage_change(int(current[key]), int(previous[key])) for key in keys},
        'previous_start': previous_start, 'previous_end': previous_end,
    }

def format_comparison(report, language='fa'):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    labels = ('دریافتی', 'هزینه', 'خالص گردش وجوه') if language == 'fa' else ('Receipts', 'Expenses', 'Net cash movement')
    keys = ('receipts', 'expenses', 'net_cash_movement')
    result = []
    for label, key in zip(labels, keys):
        change = report['changes'][key]
        indicator = ('جدید' if language == 'fa' else 'new') if change is None else f'{change:+.1f}%'
        result.append((label, report['current'][key], report['previous'][key], indicator))
    return result
