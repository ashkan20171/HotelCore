"""SQLite-backed login throttling with UTC timestamps; no account enumeration."""
import sqlite3
from datetime import datetime, timezone, timedelta
MAX_FAILURES = 5
LOCK_MINUTES = 15

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS login_attempts (
        username TEXT PRIMARY KEY, failures INTEGER NOT NULL DEFAULT 0,
        locked_until TEXT, last_failure TEXT)""")

def _now(now=None):
    return now or datetime.now(timezone.utc)

def is_locked(conn, username, now=None):
    migrate(conn)
    row=conn.execute('SELECT locked_until FROM login_attempts WHERE username=?',(username,)).fetchone()
    if not row or not row[0]: return False
    return datetime.fromisoformat(row[0]) > _now(now)

def record_failure(conn, username, now=None):
    migrate(conn)
    now=_now(now)
    row=conn.execute('SELECT failures,locked_until FROM login_attempts WHERE username=?',(username,)).fetchone()
    if row and row[1] and datetime.fromisoformat(row[1]) > now:
        return True
    count=(row[0] if row and not row[1] else 0)+1
    until=(now+timedelta(minutes=LOCK_MINUTES)).isoformat() if count>=MAX_FAILURES else None
    conn.execute("""INSERT INTO login_attempts(username,failures,locked_until,last_failure)
        VALUES(?,?,?,?) ON CONFLICT(username) DO UPDATE SET failures=excluded.failures,
        locked_until=excluded.locked_until,last_failure=excluded.last_failure""",
        (username,count,until,now.isoformat()))
    return until is not None

def clear_failures(conn, username):
    migrate(conn)
    conn.execute('DELETE FROM login_attempts WHERE username=?',(username,))


# Stage 165: append-only security telemetry for authentication outcomes.
def migrate_security_events(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS login_security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempted_username TEXT NOT NULL,
        outcome TEXT NOT NULL CHECK(outcome IN ('failure','locked','success')),
        occurred_at TEXT NOT NULL,
        detail TEXT NOT NULL DEFAULT ''
    )""")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_login_security_events_time ON login_security_events(occurred_at DESC,id DESC)')

def record_security_event(conn, username, outcome, now=None, detail=''):
    """Store an authentication outcome without ever storing credentials.

    Username is trimmed and bounded; detail is a small fixed-category field, not
    free-form exception text. Call within the same transaction as auth handling.
    """
    if outcome not in ('failure','locked','success'):
        raise ValueError('Unsupported authentication outcome')
    name=str(username or '').strip()[:128] or '<empty>'
    safe_detail=str(detail or '').strip()[:40]
    stamp=_now(now).isoformat()
    migrate_security_events(conn)
    conn.execute('INSERT INTO login_security_events(attempted_username,outcome,occurred_at,detail) VALUES(?,?,?,?)',
                 (name,outcome,stamp,safe_detail))

def recent_security_events(conn, limit=100, outcome=None):
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('limit must be between 1 and 1000')
    if outcome is not None and outcome not in ('failure','locked','success'):
        raise ValueError('Unsupported authentication outcome')
    migrate_security_events(conn)
    if outcome is None:
        rows=conn.execute('SELECT id,attempted_username,outcome,occurred_at,detail FROM login_security_events ORDER BY occurred_at DESC,id DESC LIMIT ?', (limit,)).fetchall()
    else:
        rows=conn.execute('SELECT id,attempted_username,outcome,occurred_at,detail FROM login_security_events WHERE outcome=? ORDER BY occurred_at DESC,id DESC LIMIT ?', (outcome,limit)).fetchall()
    keys=('id','attempted_username','outcome','occurred_at','detail')
    return [dict(zip(keys,row)) for row in rows]
