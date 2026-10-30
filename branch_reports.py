"""Read-only, branch-scoped operational reporting. Date interval is [start, end)."""
from datetime import date

def _validate(conn, branch_id, start, end):
    if not isinstance(branch_id, int) or not conn.execute('SELECT 1 FROM branches WHERE id=? AND active=1', (branch_id,)).fetchone():
        raise ValueError('شعبه فعال انتخاب نشده است')
    if date.fromisoformat(start) >= date.fromisoformat(end):
        raise ValueError('بازه تاریخ نامعتبر است')

def branch_reservations(conn, branch_id, start, end):
    _validate(conn, branch_id, start, end)
    return conn.execute("""SELECT r.id, rm.number, g.name, r.checkin, r.checkout
      FROM reservations r JOIN rooms rm ON rm.id=r.room_id JOIN guests g ON g.id=r.guest_id
      WHERE r.branch_id=? AND r.checkin<? AND r.checkout>? AND r.status<>'لغو شده'
      ORDER BY r.checkin,r.id""", (branch_id,end,start)).fetchall()

def branch_summary(conn, branch_id, start, end):
    _validate(conn, branch_id, start, end)
    rooms=conn.execute('SELECT COUNT(*) FROM rooms WHERE branch_id=? AND status=?', (branch_id,'فعال')).fetchone()[0]
    reservations=conn.execute("""SELECT r.id,r.checkin,r.checkout FROM reservations r
      JOIN rooms rm ON rm.id=r.room_id WHERE r.branch_id=? AND r.checkin<?
      AND r.checkout>? AND r.status<>'لغو شده'""",(branch_id,end,start)).fetchall()
    nights=sum((min(date.fromisoformat(out),date.fromisoformat(end)) - max(date.fromisoformat(inn),date.fromisoformat(start))).days for _,inn,out in reservations)
    paid=conn.execute("""SELECT COALESCE(SUM(p.amount),0) FROM payments p
      JOIN reservations r ON r.id=p.reservation_id JOIN rooms rm ON rm.id=r.room_id
      WHERE r.branch_id=? AND date(p.created_at)>=? AND date(p.created_at)<?""",(branch_id,start,end)).fetchone()[0]
    return dict(rooms=rooms,reservations=len(reservations),occupied_nights=nights,payments=paid)
