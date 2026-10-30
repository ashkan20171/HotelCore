"""Pure, testable hotel invoice calculations and schema migrations."""
from datetime import date
import sqlite3


def migrate(conn: sqlite3.Connection) -> None:
    from pricing import migrate_booking_rates
    migrate_booking_rates(conn)
    conn.execute("""CREATE TABLE IF NOT EXISTS reservation_adjustments (
        reservation_id INTEGER PRIMARY KEY REFERENCES reservations(id),
        discount_code TEXT, discount_percent INTEGER NOT NULL DEFAULT 0
            CHECK(discount_percent BETWEEN 0 AND 100),
        tax_percent INTEGER NOT NULL DEFAULT 0
            CHECK(tax_percent BETWEEN 0 AND 100),
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")


def calculate_invoice(conn: sqlite3.Connection, reservation_id: int) -> dict:
    row = conn.execute("""SELECT r.id,g.name,ro.number,r.checkin,r.checkout,ro.rate,r.status
        FROM reservations r JOIN guests g ON g.id=r.guest_id
        JOIN rooms ro ON ro.id=r.room_id WHERE r.id=?""", (reservation_id,)).fetchone()
    if row is None:
        raise ValueError('رزرو پیدا نشد')
    rid,guest,room,start,end,rate,status = row
    nights=(date.fromisoformat(end)-date.fromisoformat(start)).days
    if nights <= 0: raise ValueError('بازه اقامت نامعتبر است')
    services=conn.execute('SELECT COALESCE(SUM(quantity*unit_price),0) FROM service_orders WHERE reservation_id=?',(rid,)).fetchone()[0]
    paid=conn.execute('SELECT COALESCE(SUM(amount),0) FROM payments WHERE reservation_id=?',(rid,)).fetchone()[0]
    adj=conn.execute('SELECT discount_code,discount_percent,tax_percent FROM reservation_adjustments WHERE reservation_id=?',(rid,)).fetchone() or (None,0,0)
    code,discount_percent,tax_percent=adj
    quoted=conn.execute('SELECT accommodation_total FROM booking_rates WHERE reservation_id=?',(rid,)).fetchone()
    accommodation=quoted[0] if quoted else nights*rate
    subtotal=accommodation+services
    discount=subtotal*discount_percent//100
    taxable=subtotal-discount
    tax=taxable*tax_percent//100
    total=taxable+tax
    return dict(id=rid,guest=guest,room=room,start=start,end=end,rate=rate,status=status,nights=nights,
                services=services,accommodation=accommodation,subtotal=subtotal,code=code,discount_percent=discount_percent,
                discount=discount,tax_percent=tax_percent,tax=tax,total=total,paid=paid,balance=total-paid)


def apply_adjustment(conn: sqlite3.Connection, reservation_id: int, code: str, tax_percent: int) -> None:
    if not isinstance(tax_percent,int) or not 0 <= tax_percent <= 100:
        raise ValueError('درصد مالیات نامعتبر است')
    if conn.execute('SELECT 1 FROM reservations WHERE id=?',(reservation_id,)).fetchone() is None:
        raise ValueError('رزرو یافت نشد')
    code=code.strip().upper()
    if code:
        row=conn.execute('SELECT percent FROM discounts WHERE code=? AND active=1',(code,)).fetchone()
        if row is None: raise ValueError('کد تخفیف معتبر یا فعال نیست')
        percent=row[0]
    else: percent=0
    conn.execute("""INSERT INTO reservation_adjustments(reservation_id,discount_code,discount_percent,tax_percent)
       VALUES(?,?,?,?) ON CONFLICT(reservation_id) DO UPDATE SET
       discount_code=excluded.discount_code,discount_percent=excluded.discount_percent,
       tax_percent=excluded.tax_percent,updated_at=CURRENT_TIMESTAMP""",(reservation_id,code or None,percent,tax_percent))
