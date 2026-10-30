"""Seasonal nightly rate rules; ISO dates and integer Toman amounts."""
from datetime import date, timedelta

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS seasonal_rates (
      id INTEGER PRIMARY KEY, room_kind TEXT NOT NULL,
      start_date TEXT NOT NULL, end_date TEXT NOT NULL,
      multiplier_percent INTEGER NOT NULL CHECK(multiplier_percent BETWEEN 50 AND 300),
      CHECK(end_date > start_date))''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_seasonal_rates_dates ON seasonal_rates(start_date,end_date)')

def calculate_stay(base_rate, room_kind, checkin, checkout, rules):
    """Return total and daily details; latest matching rule in input wins."""
    start, end = date.fromisoformat(checkin), date.fromisoformat(checkout)
    if end <= start or base_rate < 0:
        raise ValueError('Invalid stay dates or base rate')
    details = []
    day = start
    while day < end:
        percent = 100
        for kind, begin, finish, pct in rules:
            if kind in (room_kind, 'همه') and begin <= day.isoformat() < finish:
                percent = pct
        amount = (base_rate * percent + 50) // 100
        details.append((day.isoformat(), amount, percent))
        day += timedelta(days=1)
    return sum(item[1] for item in details), details

def upcoming_departures(conn, today, horizon=2):
    until = (date.fromisoformat(today) + timedelta(days=horizon)).isoformat()
    return conn.execute('''SELECT r.id, g.name, rooms.number, r.checkout FROM reservations r
      JOIN guests g ON g.id=r.guest_id JOIN rooms ON rooms.id=r.room_id
      WHERE r.status='پذیرش شده' AND r.checkout>=? AND r.checkout<=?
      ORDER BY r.checkout,rooms.number''', (today, until)).fetchall()


def migrate_booking_rates(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS booking_rates (
      reservation_id INTEGER PRIMARY KEY REFERENCES reservations(id) ON DELETE CASCADE,
      accommodation_total INTEGER NOT NULL CHECK(accommodation_total >= 0),
      calculated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")

def quote_reservation(conn, room_id, start, end):
    room = conn.execute("SELECT kind,rate FROM rooms WHERE id=? AND status='فعال'", (room_id,)).fetchone()
    if not room: raise ValueError('اتاق فعال یافت نشد')
    rules = conn.execute('SELECT room_kind,start_date,end_date,multiplier_percent FROM seasonal_rates ORDER BY id').fetchall()
    return calculate_stay(room[1],room[0],start,end,rules)[0]

def save_quote(conn, reservation_id, amount):
    conn.execute('INSERT INTO booking_rates(reservation_id,accommodation_total) VALUES(?,?) ON CONFLICT(reservation_id) DO UPDATE SET accommodation_total=excluded.accommodation_total,calculated_at=CURRENT_TIMESTAMP',(reservation_id,amount))

def reschedule(conn, reservation_id, room_id, start, end):
    if end <= start: raise ValueError('تاریخ خروج باید پس از ورود باشد')
    row=conn.execute('SELECT status FROM reservations WHERE id=?',(reservation_id,)).fetchone()
    if row is None: raise ValueError('رزرو یافت نشد')
    if row[0] != 'رزرو شده': raise ValueError('فقط رزروهای پذیرش‌نشده قابل تغییر هستند')
    overlap=conn.execute("""SELECT 1 FROM reservations WHERE room_id=? AND id<>? AND status IN ('رزرو شده','پذیرش شده') AND checkin<? AND checkout>? LIMIT 1""",(room_id,reservation_id,end,start)).fetchone()
    if overlap: raise ValueError('تداخل زمانی با رزرو دیگر')
    total=quote_reservation(conn,room_id,start,end)
    conn.execute('UPDATE reservations SET room_id=?,checkin=?,checkout=? WHERE id=?',(room_id,start,end,reservation_id))
    save_quote(conn,reservation_id,total)
    return total
