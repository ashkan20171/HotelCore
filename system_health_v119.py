"""Admin-only, on-demand system health snapshot with bounded persisted check history."""
from datetime import datetime, timezone
from user_access_management import _actor


def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS system_health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checked_at TEXT NOT NULL,
        database_status TEXT NOT NULL CHECK(database_status IN ('ok','warning')),
        monitor_state TEXT NOT NULL,
        failure_count INTEGER NOT NULL CHECK(failure_count >= 0))""")


def snapshot(conn, actor_id, *, monitor_state='unknown', now=None, save=True):
    _actor(conn, actor_id)
    if not isinstance(monitor_state, str) or not 1 <= len(monitor_state) <= 64:
        raise ValueError('invalid monitor state')
    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError('timezone required')
    # SQLite quick_check provides a lightweight database consistency signal.
    check = conn.execute('PRAGMA quick_check(1)').fetchone()
    database_status = 'ok' if check and check[0] == 'ok' else 'warning'
    from security_monitor_status_v118 import migrate as migrate_failures
    migrate_failures(conn)
    failure_count = conn.execute('SELECT COUNT(*) FROM security_monitor_failures').fetchone()[0]
    migrate(conn)
    previous = conn.execute("""SELECT checked_at FROM system_health_checks
                                WHERE database_status='ok' ORDER BY id DESC LIMIT 1""").fetchone()
    result = {'database_status': database_status, 'monitor_state': monitor_state,
              'failure_count': failure_count, 'last_healthy_check': previous[0] if previous else None,
              'checked_at': timestamp.astimezone(timezone.utc).isoformat()}
    if save:
        conn.execute('INSERT INTO system_health_checks(checked_at,database_status,monitor_state,failure_count) VALUES(?,?,?,?)',
                     (result['checked_at'],database_status,monitor_state,failure_count))
        conn.execute('DELETE FROM system_health_checks WHERE id NOT IN (SELECT id FROM system_health_checks ORDER BY id DESC LIMIT 500)')
        if database_status == 'ok':
            result['last_healthy_check'] = result['checked_at']
    return result


def history(conn, actor_id, limit=25):
    _actor(conn, actor_id)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('limit must be between 1 and 100')
    migrate(conn)
    return conn.execute('SELECT checked_at,database_status,monitor_state,failure_count FROM system_health_checks ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
