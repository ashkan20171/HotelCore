"""Booking creation pace, not future occupancy or statistical demand forecasting."""
from datetime import date,timedelta

def booking_pace(conn, end, days=30):
    if type(end) is not date or type(days) is not int or not 7 <= days <= 90:
        raise ValueError('Invalid pace window')
    start=end-timedelta(days=days-1)
    prior=start-timedelta(days=days)
    rows=conn.execute("""SELECT substr(created_at,1,10) AS day,COUNT(*) FROM reservations
        WHERE created_at>=? AND created_at<? AND created_at IS NOT NULL
        GROUP BY substr(created_at,1,10)""",(prior.isoformat(),(end+timedelta(days=1)).isoformat())).fetchall()
    counts={str(day):int(count) for day,count in rows if day is not None}
    current=[{'date':(start+timedelta(days=i)).isoformat(),'new_reservations':counts.get((start+timedelta(days=i)).isoformat(),0)} for i in range(days)]
    previous=sum(counts.get((prior+timedelta(days=i)).isoformat(),0) for i in range(days))
    total=sum(row['new_reservations'] for row in current)
    change=None if previous==0 else round((total-previous)*100/previous,1)
    return {'rows':current,'current_total':total,'previous_total':previous,'change_percent':change,
            'daily_average':round(total/days,2),'peak_daily':max((row['new_reservations'] for row in current),default=0),
            'window_start':start.isoformat(),'window_end':end.isoformat(),
            'note':'Includes all created reservations, including subsequently cancelled reservations.'}

def pace_alerts(result,minimum_daily=1.0):
    if type(minimum_daily) not in (int,float) or not 0<=minimum_daily<=100000:
        raise ValueError('Invalid alert threshold')
    alerts=[]
    if result['daily_average']<minimum_daily:
        alerts.append('low_booking_creation_rate')
    if result['change_percent'] is not None and result['change_percent']<=-25:
        alerts.append('booking_creation_decline')
    return alerts
