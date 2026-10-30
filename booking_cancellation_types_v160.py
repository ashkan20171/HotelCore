"""Cancellation status by room category, grouped by booking creation time.
This does NOT infer the timestamp of cancellation or modify reservations.
"""
from datetime import date,timedelta
import csv

def cancellation_by_room_type(conn,end,days=30):
    if type(end) is not date or type(days) is not int or not 7 <= days <= 90:
        raise ValueError('Invalid reporting window')
    start=end-timedelta(days=days-1)
    rows=conn.execute("""SELECT COALESCE(NULLIF(TRIM(CAST(rooms.kind AS TEXT)),''),'Unspecified') AS room_type,
       COUNT(*) AS gross,
       SUM(CASE WHEN lower(trim(reservations.status)) IN ('cancelled','canceled','لغو شده','لغوشده') THEN 1 ELSE 0 END) AS cancelled
       FROM reservations JOIN rooms ON rooms.id=reservations.room_id
       WHERE reservations.created_at>=? AND reservations.created_at<?
       GROUP BY COALESCE(NULLIF(TRIM(CAST(rooms.kind AS TEXT)),''),'Unspecified')
       ORDER BY gross DESC,room_type ASC""",(start.isoformat(),(end+timedelta(days=1)).isoformat())).fetchall()
    result=[]
    for kind,gross,cancelled in rows:
        gross=int(gross);cancelled=int(cancelled or 0)
        result.append({'room_type':str(kind),'gross':gross,'cancelled':cancelled,
                       'net':gross-cancelled,'cancelled_pct':round(100*cancelled/gross,1) if gross else 0.0})
    return result

def export_cancellation_csv(path,rows):
    """Export only aggregate metrics; mitigate spreadsheet formula injection."""
    def safe(value):
        s=str(value)
        return "'"+s if s.lstrip().startswith(('=','+','-','@','\t','\r')) else s
    with open(path,'w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.writer(handle)
        writer.writerow(['Room type','Gross bookings','Currently cancelled','Net bookings','Cancellation share %'])
        for row in rows:
            writer.writerow([safe(row['room_type']),int(row['gross']),int(row['cancelled']),int(row['net']),float(row['cancelled_pct'])])
