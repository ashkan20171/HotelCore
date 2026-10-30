"""Authorized, date-filtered cross-branch room transfer KPIs.

Only administrators may compare multiple branches. Non-admin users can inspect
only branches explicitly assigned to them. Results never include guest PII.
"""
import csv
from collections import Counter
from datetime import date
from branch_access import allowed_branches


def compare_transfers(conn, *, user_id, role, date_from=None, date_to=None, branch_ids=None):
    if user_id is None:
        raise PermissionError('Authentication required')
    if date_from and date_to and date_from > date_to:
        raise ValueError('Start date must not exceed end date')
    for value in (date_from, date_to):
        if value:
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError('Dates must be YYYY-MM-DD') from None
    authorized = dict(allowed_branches(conn, user_id, role))
    selected = list(authorized) if branch_ids is None else list(branch_ids)
    if any(not isinstance(bid, int) or isinstance(bid, bool) or bid not in authorized for bid in selected):
        raise PermissionError('Unauthorized branch selection')
    if len(selected) > 1 and role != 'admin':
        raise PermissionError('Cross-branch comparisons require admin role')
    if not selected:
        return []
    conditions = ['branch_id IN (' + ','.join('?' for _ in selected) + ')']
    params = list(selected)
    if date_from:
        conditions.append('date(created_at)>=date(?)'); params.append(date_from)
    if date_to:
        conditions.append('date(created_at)<=date(?)'); params.append(date_to)
    try:
        events = conn.execute('SELECT branch_id,reservation_id,source_room_id,destination_room_id,actor FROM room_transfer_history WHERE '
                              + ' AND '.join(conditions), params).fetchall()
    except __import__('sqlite3').OperationalError as exc:
        if 'no such table: room_transfer_history' in str(exc):
            events = []
        else:
            raise
    result = []
    for bid in selected:
        group = [e for e in events if e[0] == bid]
        actors = Counter(str(e[4]) for e in group)
        result.append({'branch_id':bid, 'branch':authorized[bid], 'transfers':len(group),
                       'reservations':len({e[1] for e in group}),
                       'source_rooms':len({e[2] for e in group}),
                       'destination_rooms':len({e[3] for e in group}),
                       'active_staff':len(actors),
                       'top_actor':sorted(actors, key=lambda x:(-actors[x],x))[0] if actors else '—'})
    return sorted(result, key=lambda row:(-row['transfers'],row['branch_id']))


def export_comparison_csv(path, rows):
    fields = ('branch_id','branch','transfers','reservations','source_rooms','destination_rooms','active_staff','top_actor')
    with open(path,'w',newline='',encoding='utf-8-sig') as file:
        writer = csv.writer(file); writer.writerow(fields)
        for row in rows:
            writer.writerow([row[field] for field in fields])
