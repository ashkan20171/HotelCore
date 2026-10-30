"""Small painter-based comparison chart for monthly cash-flow figures."""
from math import isfinite

def chart_bars(months):
    """Normalize income/expense bars; preserve original month order."""
    if not isinstance(months,list):raise ValueError('Expected monthly rows')
    maximum=1.0
    for row in months:
        for key in ('income','expenses'):
            value=row[key]
            if type(value) not in (int,float) or not isfinite(value) or value<0:
                raise ValueError('Invalid monthly amount')
            maximum=max(maximum,float(value))
    return [{'month':str(row['month']),'income':float(row['income'])/maximum,
             'expenses':float(row['expenses'])/maximum} for row in months]
