"""Pure monitoring status/retry helpers and bounded, admin-only failure history."""
from datetime import datetime, timezone
from user_access_management import _actor

MAX_FAILURES = 1000

def retry_delay_seconds(attempt):
    if type(attempt) is not int or attempt < 1:
        raise ValueError('attempt must be a positive integer')
    return min(300, 5 * 2 ** min(attempt - 1, 6))

def classify_error(message):
    value = str(message).lower()
    if any(term in value for term in ('permissionerror', 'unauthorized', 'session', 'forbidden')):
        return 'authorization'
    if any(term in value for term in ('database is locked', 'operationalerror', 'busy')):
        return 'transient'
    return 'other'

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS security_monitor_failures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recorded_at TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('authorization','transient','other')),
        detail TEXT NOT NULL,
        retry_attempt INTEGER NOT NULL CHECK(retry_attempt>=0))''')

def record_failure(conn, actor_id, message, retry_attempt=0, now=None):
    _actor(conn, actor_id)
    if type(retry_attempt) is not int or retry_attempt < 0:
        raise ValueError('invalid retry attempt')
    category = classify_error(message)
    # Store only a bounded sanitized category, not exception text that might contain secrets.
    timestamp = (now or datetime.now(timezone.utc))
    if timestamp.tzinfo is None:
        raise ValueError('timezone required')
    migrate(conn)
    conn.execute('INSERT INTO security_monitor_failures(recorded_at,category,detail,retry_attempt) VALUES(?,?,?,?)',
                 (timestamp.astimezone(timezone.utc).isoformat(), category, category, retry_attempt))
    conn.execute('''DELETE FROM security_monitor_failures WHERE id NOT IN
                    (SELECT id FROM security_monitor_failures ORDER BY id DESC LIMIT ?)''', (MAX_FAILURES,))
    return category

def list_failures(conn, actor_id, limit=50):
    _actor(conn, actor_id)
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError('limit must be 1..200')
    migrate(conn)
    return conn.execute('''SELECT recorded_at,category,retry_attempt FROM security_monitor_failures
                           ORDER BY id DESC LIMIT ?''', (limit,)).fetchall()
