"""Pure, deterministic cash-flow filtering for screen and exports."""
from datetime import date

def filter_daily_series(series, *, search='', minimum=0, maximum=None, mode='either'):
    """Filter by date substring and selected recorded amount category.

    Mode 'either' checks the largest of receipts/expenses; 'receipts', 'expenses'
    and 'net' use their respective amounts (net may be negative).
    """
    if mode not in ('either','receipts','expenses','net'):
        raise ValueError('Unsupported filter mode')
    if type(minimum) not in (int,float) or minimum < 0:
        raise ValueError('Invalid minimum amount')
    if maximum is not None and (type(maximum) not in (int,float) or maximum < minimum):
        raise ValueError('Invalid maximum amount')
    query=str(search).strip()
    result=[]
    for row in series:
        if not isinstance(row,dict):raise ValueError('Invalid row')
        day=date.fromisoformat(row['date']).isoformat()
        receipts=row['income'];expenses=row['expenses']
        if type(receipts) not in (int,float) or type(expenses) not in (int,float):
            raise ValueError('Invalid amounts')
        amount={'either':max(receipts,expenses),'receipts':receipts,'expenses':expenses,'net':receipts-expenses}[mode]
        if query and query not in day:continue
        if amount < minimum or (maximum is not None and amount > maximum):continue
        result.append(dict(row))
    return result

def filtered_snapshot(snapshot, **filters):
    """Produce an isolated filtered copy; do not mutate authorized source."""
    data=dict(snapshot)
    data['series']=filter_daily_series(snapshot['series'],**filters)
    return data
