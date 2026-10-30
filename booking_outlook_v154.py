"""Forward-looking confirmed reservation coverage, not a statistical forecast."""
from datetime import date,timedelta

def booking_outlook(conn,start,days=30,low_threshold=30):
    if not isinstance(start,date) or type(days) is not int or not 1<=days<=90:
        raise ValueError('Invalid booking outlook period')
    if type(low_threshold) is not int or not 0<=low_threshold<=100:
        raise ValueError('Invalid low-demand threshold')
    rooms=int(conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0])
    end=start+timedelta(days=days)
    bookings=conn.execute("""SELECT checkin,checkout,room_id FROM reservations
        WHERE checkin<? AND checkout>? AND LOWER(COALESCE(status,'')) NOT LIKE '%cancel%'
        AND COALESCE(status,'') NOT LIKE '%لغو%' """,(end.isoformat(),start.isoformat())).fetchall()
    occupied=[set() for _ in range(days)]
    for checkin,checkout,room_id in bookings:
        if room_id is None:continue
        try:
            a=max(0,(date.fromisoformat(checkin)-start).days)
            b=min(days,(date.fromisoformat(checkout)-start).days)
        except (ValueError,TypeError):continue
        for index in range(a,b):occupied[index].add(room_id)
    result=[]
    for i,ids in enumerate(occupied):
        count=min(rooms,len(ids))
        percent=round(100*count/rooms,1) if rooms else 0.0
        result.append({'date':(start+timedelta(days=i)).isoformat(), 'booked_rooms':count,
                       'total_rooms':rooms,'booked_pct':percent,
                       'low_demand':bool(rooms and percent<low_threshold)})
    return result

def outlook_summary(rows):
    if not rows:return {'days':0,'average_booked_pct':0.0,'low_demand_days':0,'peak_booked_pct':0.0}
    return {'days':len(rows),'average_booked_pct':round(sum(x['booked_pct'] for x in rows)/len(rows),1),
            'low_demand_days':sum(bool(x['low_demand']) for x in rows),
            'peak_booked_pct':max(x['booked_pct'] for x in rows)}
