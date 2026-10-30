"""Booked-room value estimates. NOT realized revenue or accounting ADR/RevPAR."""
from datetime import date,timedelta

def room_value_by_type(conn,start,end):
    if not isinstance(start,date) or not isinstance(end,date) or start>end:
        raise ValueError('Invalid reporting dates')
    exclusive=(end+timedelta(days=1)).isoformat()
    rows=conn.execute("""SELECT r.kind, COUNT(DISTINCT r.id), COALESCE(SUM(CASE WHEN b.id IS NULL THEN 0 ELSE MAX(0,julianday(MIN(b.checkout,?))-julianday(MAX(b.checkin,?))) END),0),
        COALESCE(SUM(CASE WHEN b.id IS NULL THEN 0 ELSE MAX(0,julianday(MIN(b.checkout,?))-julianday(MAX(b.checkin,?)))*r.rate END),0)
        FROM rooms r LEFT JOIN reservations b ON b.room_id=r.id AND b.checkin<? AND b.checkout>?
        AND LOWER(COALESCE(b.status,'')) NOT LIKE '%cancel%' AND COALESCE(b.status,'') NOT LIKE '%لغو%'
        GROUP BY r.kind ORDER BY r.kind""",(exclusive,start.isoformat(),exclusive,start.isoformat(),exclusive,start.isoformat())).fetchall()
    days=(end-start).days+1
    output=[]
    for kind,rooms,nights,value in rows:
        available=rooms*days
        output.append({'type':kind,'rooms':rooms,'available_days':days,'booked_nights':round(float(nights),2),
                       'booked_value':round(float(value),2),
                       'estimated_adr':round(float(value)/nights,2) if nights else 0,
                       'estimated_revpar':round(float(value)/available,2) if available else 0,
                       'occupancy_pct':round(float(nights)/available*100,1) if available else 0})
    return output
