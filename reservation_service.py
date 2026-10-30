"""Transactional reservation creation; no Qt dependency."""
import sqlite3
from reservation_validation import validate_booking
from branch_operations import require_room
from pricing import quote_reservation, save_quote

def create_reservation(conn, *, user_id, role, branch_id, room_id, name, phone, national_id, checkin, checkout):
    errors = validate_booking(name, phone, room_id, checkin, checkout)
    if errors:
        raise ValueError("؛ ".join(errors.values()))
    # BEGIN IMMEDIATE obtains the SQLite writer reservation before checking overlaps.
    # Caller supplies a dedicated connection and must not start a transaction first.
    if conn.in_transaction:
        raise RuntimeError("برای ثبت رزرو، اتصال بدون تراکنش فعال لازم است")
    conn.execute("BEGIN IMMEDIATE")
    try:
        require_room(conn, user_id, role, branch_id, room_id)
        collision = conn.execute("""SELECT 1 FROM reservations
            WHERE room_id=? AND status IN ('رزرو شده','پذیرش شده')
              AND checkin < ? AND checkout > ? LIMIT 1""", (room_id, checkout, checkin)).fetchone()
        if collision:
            raise ValueError("اتاق در بازه انتخاب‌شده رزرو شده است")
        quote = quote_reservation(conn, room_id, checkin, checkout)
        guest_id = conn.execute("INSERT INTO guests(name,phone,national_id) VALUES(?,?,?)",
                                (name.strip(),phone.strip(),national_id.strip())).lastrowid
        reservation_id = conn.execute("""INSERT INTO reservations(room_id,guest_id,checkin,checkout,branch_id)
                                       VALUES(?,?,?,?,?)""", (room_id,guest_id,checkin,checkout,branch_id)).lastrowid
        save_quote(conn,reservation_id,quote)
        conn.commit()
        return reservation_id
    except Exception:
        conn.rollback()
        raise
