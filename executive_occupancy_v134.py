"""Read-only daily reservation occupancy with bounded dates and deterministic alerts."""
from datetime import date,timedelta

def daily_occupancy(conn,start,end):
    if not isinstance(start,date) or not isinstance(end,date) or start>end or (end-start).days>=90:
        raise ValueError('Invalid occupancy period')
    rooms=conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    # Count distinct rooms rather than overlapping reservations: never exceed 100%.
    rows=conn.execute("""SELECT checkin,checkout,room_id FROM reservations
        WHERE checkin<? AND checkout>? AND LOWER(COALESCE(status,'')) NOT LIKE '%cancel%'
        AND COALESCE(status,'') NOT LIKE '%لغو%'""",
        ((end+timedelta(days=1)).isoformat(),start.isoformat())).fetchall()
    result=[]
    for n in range((end-start).days+1):
        day=(start+timedelta(days=n)).isoformat()
        active={room for checkin,checkout,room in rows if checkin<=day<checkout and room is not None}
        count=min(rooms,len(active))
        result.append({'date':day,'occupied':count,'rooms':rooms,
                       'occupancy_pct':round(100*count/rooms,1) if rooms else 0.0})
    return result

def management_alerts(current,previous,*,low_occupancy=30,high_expense_ratio=90,receipts_decline=20):
    if not all(isinstance(x,dict) for x in (current,previous)):
        raise ValueError('Invalid snapshot')
    if any(type(x) is not int or x<0 or x>100 for x in (low_occupancy,high_expense_ratio,receipts_decline)):
        raise ValueError('Invalid alert thresholds')
    alerts=[]
    if current.get('room_count',0)>0 and current.get('occupancy_pct',0)<low_occupancy:
        alerts.append('low_occupancy')
    income=float(current.get('income',0));expense=float(current.get('expenses',0))
    if expense>0 and (income<=0 or expense/income*100>=high_expense_ratio):
        alerts.append('high_expense_ratio')
    if float(previous.get('income',0))>0 and income<float(previous['income'])*(1-receipts_decline/100):
        alerts.append('receipts_decline')
    return alerts
