"""Gross vs currently cancelled reservation creation cohorts (not cancellation event timing)."""
from datetime import date,timedelta

def creation_cohorts(conn,end,days=30):
    if type(end) is not date or type(days) is not int or not 7 <= days <= 90:
        raise ValueError('Invalid cohort window')
    start=end-timedelta(days=days-1)
    prior=start-timedelta(days=days)
    rows=conn.execute("""SELECT substr(created_at,1,10),
      COUNT(*), SUM(CASE WHEN lower(trim(status)) IN ('cancelled','canceled','لغو شده','لغوشده') THEN 1 ELSE 0 END)
      FROM reservations WHERE created_at >= ? AND created_at < ?
      GROUP BY substr(created_at,1,10)""",(prior.isoformat(),(end+timedelta(days=1)).isoformat())).fetchall()
    counts={str(day):(int(gross),int(cancelled or 0)) for day,gross,cancelled in rows if day is not None}
    def period(first):
        return [{'date':(first+timedelta(days=i)).isoformat(),
                 'gross':counts.get((first+timedelta(days=i)).isoformat(),(0,0))[0],
                 'cancelled':counts.get((first+timedelta(days=i)).isoformat(),(0,0))[1],
                 'net':counts.get((first+timedelta(days=i)).isoformat(),(0,0))[0]-counts.get((first+timedelta(days=i)).isoformat(),(0,0))[1]}
                for i in range(days)]
    current=period(start);previous=period(prior)
    def totals(items):
        gross=sum(r['gross'] for r in items);cancelled=sum(r['cancelled'] for r in items)
        return {'gross':gross,'cancelled':cancelled,'net':gross-cancelled,
                'cancelled_pct':round(100*cancelled/gross,1) if gross else 0.0}
    a=totals(current);b=totals(previous)
    return {'rows':current,'current':a,'previous':b,
            'net_change_pct':round(100*(a['net']-b['net'])/b['net'],1) if b['net'] else None,
            'start':start.isoformat(),'end':end.isoformat(),
            'note':'Cancelled means current reservation status, not the date of cancellation.'}

def cohort_alerts(data,minimum_daily=1.0,decline_pct=25.0,cancel_pct=30.0):
    for value in (minimum_daily,decline_pct,cancel_pct):
        if type(value) not in (float,int) or not 0<=value<=100000:
            raise ValueError('Invalid threshold')
    alerts=[]
    if data['current']['net']/len(data['rows'])<minimum_daily:alerts.append('low_net_bookings')
    if data['net_change_pct'] is not None and data['net_change_pct']<=-decline_pct:alerts.append('net_booking_decline')
    if data['current']['gross'] and data['current']['cancelled_pct']>=cancel_pct:alerts.append('high_cancellation_share')
    return alerts
