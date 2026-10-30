"""Read-only, admin-gated comparisons and threshold-based health alerts (UTC)."""
from datetime import datetime, timedelta, timezone
from user_access_management import _actor
from system_health_v119 import migrate


def _utc(value):
    if value is None:
        return datetime.now(timezone.utc)
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError('now must be a timezone-aware datetime')
    return value.astimezone(timezone.utc)


def _summary(rows):
    count = len(rows)
    warnings = sum(status != 'ok' or state in ('error','permission_error','failed','stopped') for _, status, state, _ in rows)
    return {'checks': count, 'warnings': warnings, 'warning_rate': round(warnings * 100 / count, 1) if count else 0.0,
            'max_failures': max((int(r[3]) for r in rows), default=0)}


def compare_periods(conn, actor_id, *, days=7, warning_threshold=20, now=None):
    """Compare two adjacent, nonoverlapping UTC periods. No writes except schema migration."""
    _actor(conn, actor_id)
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('days must be 1..90')
    if type(warning_threshold) is not int or not 0 <= warning_threshold <= 100:
        raise ValueError('warning_threshold must be 0..100')
    end = _utc(now)
    start = end - timedelta(days=days)
    previous_start = start - timedelta(days=days)
    migrate(conn)
    rows = conn.execute('''SELECT checked_at,database_status,monitor_state,failure_count
      FROM system_health_checks WHERE checked_at >= ? AND checked_at < ? ORDER BY checked_at''',
      (previous_start.isoformat(), end.isoformat())).fetchall()
    previous = _summary([r for r in rows if r[0] < start.isoformat()])
    current = _summary([r for r in rows if r[0] >= start.isoformat()])
    alerts = []
    if not current['checks']:
        alerts.append('no_recent_checks')
    else:
        if current['warning_rate'] >= warning_threshold and current['warnings']:
            alerts.append('warning_rate_threshold')
        if rows and rows[-1][1] != 'ok':
            alerts.append('database_warning')
        if rows and rows[-1][2] in ('error','permission_error','failed','stopped'):
            alerts.append('monitor_warning')
    return {'current': current, 'previous': previous,
            'warning_rate_delta': round(current['warning_rate'] - previous['warning_rate'], 1),
            'alerts': alerts, 'days': days, 'warning_threshold': warning_threshold,
            'period_start': start.isoformat(), 'period_end': end.isoformat()}
