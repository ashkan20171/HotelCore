"""Validated, presentation-only daily financial insights (not recognized profit)."""
from datetime import date
from math import isfinite

def daily_insight(row):
    if not isinstance(row,dict):raise ValueError('Expected daily row')
    try:
        day=date.fromisoformat(row['date'])
        if day.isoformat()!=row['date']:raise ValueError('Invalid ISO date')
        income=float(row['income']);expenses=float(row['expenses'])
    except (TypeError,KeyError,OverflowError) as exc:raise ValueError('Invalid daily row') from exc
    if not all(map(isfinite,(income,expenses))) or income<0 or expenses<0:
        raise ValueError('Daily amounts must be finite and nonnegative')
    ratio=100*expenses/income if income else None
    return {'date':day.isoformat(),'income':income,'expenses':expenses,
            'net':income-expenses,'expense_ratio_pct':ratio,
            'expense_ratio_label':f'{ratio:.1f}%' if ratio is not None else 'N/A'}
