"""Branch-scoped room-transfer reporting with parameterized filters."""
import csv


def query_transfers(conn, *, branch_id, reservation_id=None, actor=None, date_from=None, date_to=None, limit=500):
    if not isinstance(branch_id, int) or isinstance(branch_id, bool) or branch_id < 1:
        raise ValueError('Valid branch ID required')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 2000:
        raise ValueError('Limit must be between 1 and 2000')
    if reservation_id is not None and (not isinstance(reservation_id, int) or isinstance(reservation_id, bool) or reservation_id < 1):
        raise ValueError('Invalid reservation ID')
    if date_from and date_to and date_from > date_to:
        raise ValueError('Start date must not exceed end date')
    conditions=['h.branch_id=?']; params=[branch_id]
    if reservation_id is not None:
        conditions.append('h.reservation_id=?'); params.append(reservation_id)
    if actor:
        conditions.append('h.actor LIKE ?'); params.append('%'+actor.strip().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
    if date_from:
        conditions.append('date(h.created_at)>=date(?)'); params.append(date_from)
    if date_to:
        conditions.append('date(h.created_at)<=date(?)'); params.append(date_to)
    where=' AND '.join(conditions)
    sql=f"""SELECT h.id,h.created_at,h.reservation_id,
        COALESCE(src.number, CAST(h.source_room_id AS TEXT)),
        COALESCE(dst.number, CAST(h.destination_room_id AS TEXT)),h.actor
        FROM room_transfer_history h
        LEFT JOIN rooms src ON src.id=h.source_room_id
        LEFT JOIN rooms dst ON dst.id=h.destination_room_id
        WHERE {where} ORDER BY h.id DESC LIMIT ?"""
    params.append(limit)
    try:
        return conn.execute(sql,params).fetchall()
    except __import__('sqlite3').OperationalError as exc:
        if 'no such table: room_transfer_history' in str(exc): return []
        raise


def export_transfers_csv(path, rows):
    with open(path,'w',encoding='utf-8-sig',newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['ID','Timestamp','Reservation ID','Source room','Destination room','Actor'])
        writer.writerows(rows)
