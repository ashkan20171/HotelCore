"""Branch-authorized indicative stay trends; not accounting revenue."""
from datetime import date, timedelta
from revenue_occupancy_dashboard import dashboard_kpis
from stay_performance import estimated_branch_performance


def previous_window(start, end):
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if b <= a:
        raise ValueError('Invalid reporting interval')
    duration = b-a
    return (a-duration).isoformat(), a.isoformat()


def compare_periods(conn, *, branch_id, start, end, user_id, role):
    old_start, old_end = previous_window(start, end)
    arguments = dict(branch_id=branch_id, user_id=user_id, role=role)
    current = dashboard_kpis(estimated_branch_performance(conn, start=start, end=end, **arguments))
    previous = dashboard_kpis(estimated_branch_performance(conn, start=old_start, end=old_end, **arguments))
    changes = {}
    for field in ('occupancy_percent', 'estimated_adr', 'estimated_revpar', 'estimated_value'):
        a, b = current[field], previous[field]
        changes[field] = None if a is None or b is None or (field in ('estimated_adr', 'estimated_revpar') and (current['incomplete'] or previous['incomplete'])) else round(a-b, 2)
    return dict(current=current, previous=previous, changes=changes,
                previous_start=old_start, previous_end=old_end)


def daily_occupancy(conn, *, branch_id, start, end, user_id, role):
    """Daily room-night estimates using current active inventory, branch access enforced."""
    from branch_access import require_branch
    require_branch(conn, user_id, role, branch_id)
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if b <= a or (b-a).days > 366:
        raise ValueError('Reporting period must contain 1 to 366 days')
    rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE branch_id=? AND status='فعال'", (branch_id,)).fetchone()[0]
    reservations = conn.execute("""SELECT checkin,checkout FROM reservations
        WHERE branch_id=? AND status<>'لغو شده' AND checkin<? AND checkout>?""",
        (branch_id, end, start)).fetchall()
    intervals = [(date.fromisoformat(x), date.fromisoformat(y)) for x, y in reservations]
    result = []
    for offset in range((b-a).days):
        day = a+timedelta(days=offset)
        occupied = sum(x <= day < y for x,y in intervals)
        result.append(dict(date=day.isoformat(), occupied=occupied, capacity=rooms,
                           occupancy_percent=round(occupied*100/rooms, 1) if rooms else None))
    return result
