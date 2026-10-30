"""Read-only executive KPIs. All values are based on recorded data, not forecasts."""
from datetime import date,datetime,timedelta,timezone
from user_access_management import _actor


def validate(days, today):
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('Period must be between 1 and 90 days')
    if not isinstance(today,date) or isinstance(today,datetime):
        raise ValueError('Expected a calendar date')


def _period(conn, start, end):
    # Daily income/expenses are based on recorded timestamps, not stay dates.
    lo=start.isoformat()+' 00:00:00'; hi=(end+timedelta(days=1)).isoformat()+' 00:00:00'
    payments=conn.execute('SELECT COALESCE(SUM(amount),0),COUNT(*) FROM payments WHERE created_at>=? AND created_at<?',(lo,hi)).fetchone()
    expenses=conn.execute('SELECT COALESCE(SUM(amount),0),COUNT(*) FROM expenses WHERE created_at>=? AND created_at<?',(lo,hi)).fetchone()
    reservations=conn.execute('SELECT COUNT(*) FROM reservations WHERE created_at>=? AND created_at<?',(lo,hi)).fetchone()[0]
    # Occupied room-nights: reservation date overlap, exclude cancelled reservations.
    # SQLite julianday() handles ISO date strings; inclusive start, exclusive checkout.
    # Count unique room/day combinations when the production schema exposes room_id.
    # Legacy test/demo schemas without room_id retain the earlier calculation.
    columns={row[1] for row in conn.execute('PRAGMA table_info(reservations)')}
    if 'room_id' in columns:
        nights=conn.execute("""WITH RECURSIVE calendar(day) AS (
            SELECT ? UNION ALL SELECT date(day,'+1 day') FROM calendar WHERE day<?
        ) SELECT COUNT(*) FROM (
            SELECT DISTINCT r.room_id,c.day FROM reservations r
            JOIN calendar c ON r.checkin<=c.day AND r.checkout>c.day
            JOIN rooms rm ON rm.id=r.room_id
            WHERE LOWER(COALESCE(r.status,'')) NOT LIKE '%cancel%'
              AND COALESCE(r.status,'') NOT LIKE '%لغو%'
        )""",(start.isoformat(),end.isoformat())).fetchone()[0]
    else:
        nights=conn.execute("""SELECT COALESCE(SUM(MAX(0, julianday(MIN(checkout,?)) - julianday(MAX(checkin,?)))),0)
            FROM reservations WHERE checkin<? AND checkout>? AND
            LOWER(COALESCE(status,'')) NOT LIKE '%cancel%' AND COALESCE(status,'') NOT LIKE '%لغو%' """,
            ((end+timedelta(days=1)).isoformat(),start.isoformat(),(end+timedelta(days=1)).isoformat(),start.isoformat())).fetchone()[0]
    rooms=conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    available=rooms*((end-start).days+1)
    return {'income':payments[0],'payments':payments[1],'expenses':expenses[0], 'expense_count':expenses[1],
            'cash_difference':payments[0]-expenses[0], 'new_reservations':reservations,
            'occupied_nights':round(float(nights),2),'available_nights':available,
            'occupancy_pct':round(100*float(nights)/available,1) if available else 0.0,
            'room_count':rooms}


def snapshot(conn,actor_id,*,days=30,today=None,start_date=None,end_date=None):
    _actor(conn,actor_id)
    today=today or datetime.now(timezone.utc).date()
    validate(days,today)
    if start_date is not None or end_date is not None:
        if not isinstance(start_date,date) or isinstance(start_date,datetime) or not isinstance(end_date,date) or isinstance(end_date,datetime):
            raise ValueError('Both calendar dates are required')
        if end_date < start_date or end_date > today:
            raise ValueError('Invalid reporting date range')
        days=(end_date-start_date).days+1
        validate(days,today)
        today=end_date
        start=start_date
    else:
        start=today-timedelta(days=days-1)
    previous_end=start-timedelta(days=1)
    previous_start=previous_end-timedelta(days=days-1)
    current=_period(conn,start,today)
    previous=_period(conn,previous_start,previous_end)
    # One query per source for daily series, bounded to 90 days.
    lo=start.isoformat()+' 00:00:00'; hi=(today+timedelta(days=1)).isoformat()+' 00:00:00'
    def daily(table):
        return dict(conn.execute(f'SELECT substr(created_at,1,10),COALESCE(SUM(amount),0) FROM {table} WHERE created_at>=? AND created_at<? GROUP BY substr(created_at,1,10)',(lo,hi)).fetchall())
    incomes=daily('payments');costs=daily('expenses')
    series=[{'date':(start+timedelta(days=i)).isoformat(), 'income':incomes.get((start+timedelta(days=i)).isoformat(),0),
             'expenses':costs.get((start+timedelta(days=i)).isoformat(),0)} for i in range(days)]
    return {'days':days,'start':start.isoformat(),'end':today.isoformat(), 'current':current,'previous':previous,'series':series}
