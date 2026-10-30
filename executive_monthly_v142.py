"""Monthly recorded cash-flow summaries from an already authorized daily snapshot."""
from collections import defaultdict

def monthly_totals(series):
    result=defaultdict(lambda: {'income':0,'expenses':0})
    for row in series:
        month=row['date'][:7]
        if len(month)!=7 or month[4]!='-' or not month[:4].isdigit() or not month[5:].isdigit() or not 1<=int(month[5:])<=12:
            raise ValueError('Invalid ISO month')
        for key in ('income','expenses'):
            value=row[key]
            if type(value) not in (int,float) or value<0:
                raise ValueError('Invalid financial amount')
            result[month][key]+=value
    return [{'month':month,'income':values['income'],'expenses':values['expenses'], 'difference':values['income']-values['expenses']} for month,values in sorted(result.items())]
