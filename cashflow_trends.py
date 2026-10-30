"""Branch-authorized monthly cash movement trends. End date is exclusive."""
from datetime import date
from calendar import monthrange
from branch_access import allowed_branches
from branch_cashflow import cashflow


def month_intervals(start, end):
    a=date.fromisoformat(start); b=date.fromisoformat(end)
    if a>=b: raise ValueError('Invalid interval')
    current=a
    while current<b:
        if current.month==12: next_month=date(current.year+1,1,1)
        else: next_month=date(current.year,current.month+1,1)
        stop=min(b,next_month)
        yield current.isoformat(),stop.isoformat(),current.strftime('%Y-%m')
        current=stop


def monthly_cashflow(conn, *, branch_id, user_id, role, start, end):
    result=[]
    for begin,finish,month in month_intervals(start,end):
        report=cashflow(conn,branch_id=branch_id,user_id=user_id,role=role,start=begin,end=finish)
        result.append({'month':month,'start':begin,'end':finish,'receipts':int(report['receipts']),
                       'expenses':int(report['expenses']),'net':int(report['net_cash_movement'])})
    return result


def monthly_cashflow_authorized(conn, *, user_id, role, start, end):
    return [(name,monthly_cashflow(conn,branch_id=bid,user_id=user_id,role=role,start=start,end=end))
            for bid,name in allowed_branches(conn,user_id,role)]


def scale_bars(rows, *, width=100):
    if width<=0: raise ValueError('Invalid width')
    peak=max([max(r['receipts'],r['expenses']) for r in rows] or [0])
    return [{**r,'receipt_percent':round(100*r['receipts']/peak) if peak else 0,
             'expense_percent':round(100*r['expenses']/peak) if peak else 0} for r in rows]
