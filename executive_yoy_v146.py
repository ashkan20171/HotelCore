"""Compare equal-length recorded cash-flow windows, one Gregorian year apart.

A comparison is only a like-for-like date window, not an entire annual financial statement.
"""
from datetime import date, timedelta


def previous_year_window(start, end):
    if not isinstance(start, date) or not isinstance(end, date) or start > end:
        raise ValueError('Invalid date window')
    if (end-start).days >= 90:
        raise ValueError('At most 90 days')
    try:
        prior_start=start.replace(year=start.year-1)
    except ValueError:
        prior_start=start.replace(year=start.year-1,day=28)
    prior_end=prior_start+timedelta(days=(end-start).days)
    return prior_start,prior_end


def cash_totals(conn,start,end):
    if start>end:raise ValueError('Invalid dates')
    lo=start.isoformat()+' 00:00:00'
    hi=(end+timedelta(days=1)).isoformat()+' 00:00:00'
    values={}
    for table,key in (('payments','income'),('expenses','expenses')):
        values[key]=conn.execute(
            f'SELECT COALESCE(SUM(amount),0) FROM {table} WHERE created_at>=? AND created_at<?',
            (lo,hi)).fetchone()[0]
    values['difference']=values['income']-values['expenses']
    return values


def compare(current,prior):
    result={}
    for key in ('income','expenses','difference'):
        a=current[key];b=prior[key]
        if not isinstance(a,(int,float)) or not isinstance(b,(int,float)):
            raise ValueError('Non-numeric amount')
        result[key]={'current':a,'previous':b,'delta':a-b,
                     'percent':round(100*(a-b)/abs(b),1) if b else None}
    return result


def year_over_year(conn,start,end,current):
    prior_start,prior_end=previous_year_window(start,end)
    prior=cash_totals(conn,prior_start,prior_end)
    return {'prior_start':prior_start.isoformat(),'prior_end':prior_end.isoformat(),
            'metrics':compare(current,prior)}
