"""Auditable administrator-only user lifecycle operations for SQLite."""
from __future__ import annotations
import hashlib
import secrets
from first_run_security import validate_admin_credentials

ROLES=frozenset(('admin','reception'))

def migrate(conn):
    columns={r[1] for r in conn.execute('PRAGMA table_info(users)')}
    if 'active' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(active)')
    conn.execute("""CREATE TABLE IF NOT EXISTS security_events(
        id INTEGER PRIMARY KEY, actor_id INTEGER, target_id INTEGER,
        event TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    from security_sessions import migrate as migrate_sessions
    migrate_sessions(conn)

def _actor(conn,actor_id):
    row=conn.execute('SELECT role,active FROM users WHERE id=?',(actor_id,)).fetchone()
    if not row or row!=('admin',1):
        raise PermissionError('An active administrator account is required')

def _target(conn,target_id):
    row=conn.execute('SELECT username,role,active FROM users WHERE id=?',(target_id,)).fetchone()
    if not row:raise ValueError('User does not exist')
    return row

def _protect_last_admin(conn,target_id):
    username,role,active=_target(conn,target_id)
    if role=='admin' and active and conn.execute(
        "SELECT COUNT(*) FROM users WHERE role='admin' AND active=1").fetchone()[0]<=1:
        raise ValueError('Cannot disable or demote the last active administrator')

def list_accounts(conn,actor_id):
    _actor(conn,actor_id)
    return conn.execute('SELECT id,username,role,active FROM users ORDER BY username').fetchall()

def set_account_active(conn,actor_id,target_id,active):
    _actor(conn,actor_id)
    if not isinstance(active,bool):raise ValueError('Active must be a boolean')
    _target(conn,target_id)
    if not active:
        if actor_id==target_id:raise ValueError('Cannot disable your own account')
        _protect_last_admin(conn,target_id)
    conn.execute('UPDATE users SET active=? WHERE id=?',(int(active),target_id))
    if not active:
        from security_sessions import revoke_user_sessions
        revoke_user_sessions(conn,target_id)
    conn.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',
                 (actor_id,target_id,'account_enabled' if active else 'account_disabled'))

def set_account_role(conn,actor_id,target_id,role):
    _actor(conn,actor_id)
    if role not in ROLES:raise ValueError('Unsupported role')
    _,previous,_=_target(conn,target_id)
    if role!='admin' and previous=='admin':
        if actor_id==target_id:raise ValueError('Cannot demote your own account')
        _protect_last_admin(conn,target_id)
    conn.execute('UPDATE users SET role=? WHERE id=?',(role,target_id))
    from security_sessions import revoke_user_sessions
    revoke_user_sessions(conn,target_id)
    conn.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',
                 (actor_id,target_id,'role_changed'))

def reset_account_password(conn,actor_id,target_id,new_password,confirmation):
    _actor(conn,actor_id)
    username,_,_=_target(conn,target_id)
    validate_admin_credentials(username,new_password,confirmation)
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',new_password.encode(),bytes.fromhex(salt),240000).hex()
    conn.execute('UPDATE users SET password_hash=?,salt=? WHERE id=?',(digest,salt,target_id))
    from security_sessions import revoke_user_sessions
    revoke_user_sessions(conn,target_id)
    conn.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',
                 (actor_id,target_id,'password_reset'))
