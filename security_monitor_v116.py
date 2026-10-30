"""Admin-controlled, bounded security polling. No threads or external services."""
from user_access_management import _actor
from security_alerts_v113 import evaluate_and_record
from security_notifications_v114 import sync_alerts

MIN_INTERVAL = 60
MAX_INTERVAL = 3600
DEFAULT_INTERVAL = 300


def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS security_monitor_settings (
        id INTEGER PRIMARY KEY CHECK(id=1), enabled INTEGER NOT NULL DEFAULT 1
        CHECK(enabled IN (0,1)), interval_seconds INTEGER NOT NULL DEFAULT 300
        CHECK(interval_seconds BETWEEN 60 AND 3600))''')
    conn.execute('INSERT OR IGNORE INTO security_monitor_settings(id) VALUES(1)')


def get_settings(conn, actor_id):
    _actor(conn, actor_id)
    migrate(conn)
    enabled, interval = conn.execute('SELECT enabled,interval_seconds FROM security_monitor_settings WHERE id=1').fetchone()
    return {'enabled': bool(enabled), 'interval_seconds': interval}


def set_settings(conn, actor_id, *, enabled, interval_seconds):
    _actor(conn, actor_id)
    if type(enabled) is not bool:
        raise ValueError('enabled must be a boolean')
    if type(interval_seconds) is not int or not MIN_INTERVAL <= interval_seconds <= MAX_INTERVAL:
        raise ValueError('interval_seconds must be between 60 and 3600')
    migrate(conn)
    conn.execute('UPDATE security_monitor_settings SET enabled=?, interval_seconds=? WHERE id=1',
                 (int(enabled), interval_seconds))
    return get_settings(conn, actor_id)


def poll(conn, actor_id, *, now=None):
    """One atomic-ish poll: evaluate the global 7-day window and synchronize inbox.

    Caller must commit transaction; no background worker and no automatic retries.
    """
    config = get_settings(conn, actor_id)
    if not config['enabled']:
        return {'enabled': False, 'unread': None, 'alert': None}
    result = evaluate_and_record(conn, actor_id, days=7, now=now)
    count = sync_alerts(conn, actor_id)
    return {'enabled': True, 'unread': count, 'alert': result['alert']}
