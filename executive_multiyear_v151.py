"""Bounded historical cash-flow comparisons from recorded payments and expenses.

Same-length inclusive windows are anchored to Gregorian/Jalali calendar years.
This is cash movement, not accrued accounting revenue or forecast.
"""
from datetime import date, datetime, timedelta
from math import isfinite
from executive_yoy_v146 import previous_year_window
from executive_yoy_v147 import previous_jalali_year_window

MAX_YEARS = 5

def historical_windows(start, end, *, calendar='gregorian', years=MAX_YEARS):
    if calendar not in ('gregorian', 'jalali'):
        raise ValueError('Unsupported calendar')
    if type(years) is not int or not 1 <= years <= MAX_YEARS:
        raise ValueError('Years must be 1..5')
    if type(start) is not date or type(end) is not date or end < start or (end-start).days >= 90:
        raise ValueError('Invalid period (maximum 90 days)')
    shift = previous_jalali_year_window if calendar == 'jalali' else previous_year_window
    windows = [(start, end)]
    for _ in range(years):
        windows.append(shift(*windows[-1]))
    return windows

def historical_cashflow(conn, start, end, *, calendar='gregorian', years=MAX_YEARS):
    windows = historical_windows(start, end, calendar=calendar, years=years)
    output = []
    for offset, (begin, finish) in enumerate(windows):
        lower = begin.isoformat() + ' 00:00:00'
        upper = (finish + timedelta(days=1)).isoformat() + ' 00:00:00'
        amounts = {}
        for field, table in (('income','payments'),('expenses','expenses')):
            value, count = conn.execute(
                f'SELECT COALESCE(SUM(amount),0),COUNT(*) FROM {table} WHERE created_at>=? AND created_at<?',
                (lower, upper)).fetchone()
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError('Invalid financial value')
            amounts[field] = value
            amounts[field + '_count'] = count
        output.append({'years_ago':offset,'start':begin.isoformat(),'end':finish.isoformat(),
                       'income':amounts['income'],'expenses':amounts['expenses'],
                       'difference':amounts['income']-amounts['expenses'],
                       'payment_count':amounts['income_count'],
                       'expense_count':amounts['expenses_count']})
    return {'calendar':calendar, 'rows':output}
