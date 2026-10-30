"""Database-backed sessions with revocation, expiry and metadata-only audit."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hashlib
import secrets

def _now():
    return datetime.now(timezone.utc)

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS user_sessions(
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        token_digest TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        revoked_at TEXT,
        last_seen_at TEXT)""")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id,revoked_at)')
    conn.execute("""CREATE TABLE IF NOT EXISTS login_events(
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        outcome TEXT NOT NULL CHECK(outcome IN ('success','failure','locked')),
        occurred_at TEXT NOT NULL)""")

def _stamp(dt):
    return dt.astimezone(timezone.utc).isoformat()

def _digest(token):
    return hashlib.sha256(token.encode('ascii')).hexdigest()

def record_login(conn, user_id, outcome, *, now=None):
    if outcome not in ('success','failure','locked'):
        raise ValueError('Invalid login outcome')
    conn.execute('INSERT INTO login_events(user_id,outcome,occurred_at) VALUES(?,?,?)',
                 (user_id,outcome,_stamp(now or _now())))

def create_session(conn,user_id,*,now=None,lifetime_hours=12):
    if not 1<=lifetime_hours<=168:
        raise ValueError('Invalid session lifetime')
    row=conn.execute('SELECT active FROM users WHERE id=?',(user_id,)).fetchone()
    if not row or row[0]!=1:
        raise PermissionError('User is disabled or missing')
    instant=now or _now()
    token=secrets.token_urlsafe(32)
    conn.execute('INSERT INTO user_sessions(user_id,token_digest,created_at,expires_at) VALUES(?,?,?,?)',
                 (user_id,_digest(token),_stamp(instant),_stamp(instant+timedelta(hours=lifetime_hours))))
    return token

def validate_session(conn,token,*,now=None):
    if not token:
        return False
    row=conn.execute("""SELECT s.expires_at,s.revoked_at,u.active
        FROM user_sessions s JOIN users u ON u.id=s.user_id WHERE s.token_digest=?""",
        (_digest(token),)).fetchone()
    if not row or row[1] is not None or row[2]!=1:
        return False
    return datetime.fromisoformat(row[0])>(now or _now())

def touch_session(conn,token,*,now=None):
    if not validate_session(conn,token,now=now):
        raise PermissionError('Session is no longer valid')
    conn.execute('UPDATE user_sessions SET last_seen_at=? WHERE token_digest=?',
                 (_stamp(now or _now()),_digest(token)))

def revoke_user_sessions(conn,user_id,*,now=None):
    conn.execute('UPDATE user_sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL',
                 (_stamp(now or _now()),user_id))

def revoke_session(conn,token,*,now=None):
    conn.execute('UPDATE user_sessions SET revoked_at=? WHERE token_digest=? AND revoked_at IS NULL',
                 (_stamp(now or _now()),_digest(token)))

def list_sessions(conn,actor_id,target_id):
    from user_access_management import _actor
    _actor(conn,actor_id)
    return conn.execute("""SELECT id,created_at,expires_at,revoked_at,last_seen_at
        FROM user_sessions WHERE user_id=? ORDER BY id DESC LIMIT 100""",(target_id,)).fetchall()

def recent_login_events(conn,actor_id,limit=50):
    from user_access_management import _actor
    _actor(conn,actor_id)
    if not isinstance(limit,int) or not 1<=limit<=100:
        raise ValueError('Invalid limit')
    return conn.execute("""SELECT e.occurred_at,COALESCE(u.username,'—'),e.outcome
        FROM login_events e LEFT JOIN users u ON u.id=e.user_id
        ORDER BY e.id DESC LIMIT ?""",(limit,)).fetchall()
