"""Calendar-aware aggregation of recorded cash flow by actual calendar month."""
from collections import defaultdict
from datetime import date
from math import isfinite

def monthly_totals(series,calendar='gregorian'):
    if calendar not in ('gregorian','jalali'):
        raise ValueError('Unsupported calendar')
    converter=None
    if calendar=='jalali':
        import jdatetime
        converter=jdatetime.date.fromgregorian
    totals=defaultdict(lambda:{'income':0,'expenses':0})
    for row in series:
        if not isinstance(row,dict):raise ValueError('Invalid daily row')
        try:day=date.fromisoformat(row['date'])
        except (ValueError,TypeError,KeyError) as exc:raise ValueError('Invalid ISO date') from exc
        if converter:
            solar=converter(date=day)
            key=f'{solar.year:04d}/{solar.month:02d}'
        else:key=f'{day.year:04d}-{day.month:02d}'
        for field in ('income','expenses'):
            amount=row.get(field)
            if type(amount) not in (int,float) or not isfinite(amount) or amount<0:
                raise ValueError('Invalid financial amount')
            totals[key][field]+=amount
    return [{'month':month,'income':item['income'],'expenses':item['expenses'],
             'difference':item['income']-item['expenses']}
            for month,item in sorted(totals.items())]
