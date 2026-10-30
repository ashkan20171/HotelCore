"""Atomic, branch-scoped room transfer with conflict detection and audit trail."""
from datetime import date
from branch_guard import authorize_reservation
from branch_operations import require_room
from pricing import reschedule


def transfer_booking(conn, *, user_id, role, branch_id, reservation_id, destination_room_id, actor='system'):
    if conn.in_transaction:
        raise RuntimeError('Room transfer requires a connection without an active transaction')
    conn.execute('BEGIN IMMEDIATE')
    try:
        authorize_reservation(conn,user_id,role,branch_id,reservation_id)
        require_room(conn,user_id,role,branch_id,destination_room_id)
        row=conn.execute('SELECT room_id,checkin,checkout,status FROM reservations WHERE id=? AND branch_id=?',
                         (reservation_id,branch_id)).fetchone()
        if not row: raise ValueError('Reservation not found')
        source, start, end, status=row
        if status!='رزرو شده': raise ValueError('Only pending reservations can be transferred')
        if source==destination_room_id: raise ValueError('Destination must differ from the current room')
        if date.fromisoformat(end)<=date.fromisoformat(start): raise ValueError('Invalid reservation dates')
        total=reschedule(conn,reservation_id,destination_room_id,start,end)
        conn.execute("""CREATE TABLE IF NOT EXISTS room_transfer_history (
          id INTEGER PRIMARY KEY, reservation_id INTEGER NOT NULL,
          source_room_id INTEGER NOT NULL, destination_room_id INTEGER NOT NULL,
          branch_id INTEGER NOT NULL, actor TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        conn.execute('INSERT INTO room_transfer_history(reservation_id,source_room_id,destination_room_id,branch_id,actor) VALUES(?,?,?,?,?)',
                     (reservation_id,source,destination_room_id,branch_id,str(actor)))
        conn.commit()
        return total
    except Exception:
        conn.rollback()
        raise
