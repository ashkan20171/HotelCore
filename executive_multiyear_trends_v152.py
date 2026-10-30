"""Presentation-only multi-year cash-flow comparisons (no fabricated data)."""
from math import isfinite

def growth_percent(current, previous):
    """Return None when growth cannot be defined from a zero baseline."""
    if any(type(v) not in (int,float) or not isfinite(v) for v in (current,previous)):
        raise ValueError('Invalid financial value')
    if previous == 0:
        return None
    return round((current-previous)*100/abs(previous),2)

def historical_trends(rows):
    """Chronological (oldest first) points, growth vs the immediately prior year."""
    if not isinstance(rows,list) or not 1<=len(rows)<=5:
        raise ValueError('Expected one to five historical periods')
    years=set();output=[]
    for row in sorted(rows,key=lambda r:r['years_ago'],reverse=True):
        age=row['years_ago']
        if type(age) is not int or age<0 or age in years:
            raise ValueError('Invalid period index')
        years.add(age)
        values={}
        for key in ('income','expenses','difference'):
            value=row[key]
            if type(value) not in (int,float) or not isfinite(value):
                raise ValueError('Invalid financial value')
            values[key]=value
        values.update(years_ago=age,start=row['start'],end=row['end'])
        values['income_growth_pct']=growth_percent(values['income'],output[-1]['income']) if output else None
        values['expense_growth_pct']=growth_percent(values['expenses'],output[-1]['expenses']) if output else None
        output.append(values)
    return output
