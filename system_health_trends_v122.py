"""Admin-gated, read-only UTC daily health trends for the selected window."""
from datetime import datetime, timedelta, timezone
from user_access_management import _actor
from system_health_v119 import migrate


def daily_trends(conn, actor_id, *, days=7, now=None):
    _actor(conn, actor_id)
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('days must be 1..90')
    end = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(end, datetime) or end.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    end = end.astimezone(timezone.utc)
    start = end - timedelta(days=days)
    migrate(conn)
    rows = conn.execute("""SELECT checked_at,database_status,monitor_state FROM system_health_checks
       WHERE checked_at >= ? AND checked_at < ? ORDER BY checked_at""",
       (start.isoformat(), end.isoformat())).fetchall()
    buckets = {}
    for checked_at, database_status, monitor_state in rows:
        try:
            when = datetime.fromisoformat(checked_at)
            if when.tzinfo is None: continue
            when = when.astimezone(timezone.utc)
        except (ValueError, TypeError):
            continue
        if not start <= when < end: continue
        day = when.date().isoformat()
        bucket = buckets.setdefault(day, {'date':day,'checks':0,'warnings':0})
        bucket['checks'] += 1
        if database_status != 'ok' or monitor_state in ('error','permission_error','failed','stopped'):
            bucket['warnings'] += 1
    first_day = start.date()
    count = (end.date() - first_day).days + 1
    result = []
    for i in range(count):
        day = (first_day + timedelta(days=i)).isoformat()
        result.append(buckets.get(day, {'date':day,'checks':0,'warnings':0}))
    return result
