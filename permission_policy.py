"""Fine-grained, fail-closed user permission overrides with audit trail.

Admin capabilities cannot be delegated to reception users. The admin role always
retains its base permissions; user overrides affect only non-admin permissions.
"""
from security_overview import ROLE_PERMISSIONS
from user_access_management import _actor
from security_sessions import revoke_user_sessions

ALL_PERMISSIONS = frozenset().union(*ROLE_PERMISSIONS.values())
ADMIN_RESERVED = frozenset({'users.manage','security.view','security.revoke','finance.manage','branches.manage'})

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS user_permission_overrides (
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        permission TEXT NOT NULL,
        allowed INTEGER NOT NULL CHECK(allowed IN (0,1)),
        PRIMARY KEY(user_id,permission))''')

def effective_permissions(conn,user_id):
    row=conn.execute('SELECT role,active FROM users WHERE id=?',(user_id,)).fetchone()
    if not row or row[1]!=1:return frozenset()
    migrate(conn)
    role=row[0]
    result=set(ROLE_PERMISSIONS.get(role,frozenset()))
    if role=='admin':return frozenset(result)
    for permission,allowed in conn.execute('SELECT permission,allowed FROM user_permission_overrides WHERE user_id=?',(user_id,)):
        if permission in ALL_PERMISSIONS and permission not in ADMIN_RESERVED:
            if allowed:result.add(permission)
            else:result.discard(permission)
    return frozenset(result)

def require_user_permission(conn,user_id,permission):
    if permission not in ALL_PERMISSIONS:raise ValueError('Unknown permission')
    if permission not in effective_permissions(conn,user_id):raise PermissionError('Insufficient permissions')
    return True

def get_overrides(conn,actor_id,target_id):
    _actor(conn,actor_id)
    if not conn.execute('SELECT 1 FROM users WHERE id=?',(target_id,)).fetchone():
        raise ValueError('User does not exist')
    return dict(conn.execute('SELECT permission,allowed FROM user_permission_overrides WHERE user_id=?',(target_id,)))

def set_override(conn,actor_id,target_id,permission,allowed):
    _actor(conn,actor_id)
    if permission not in ALL_PERMISSIONS:raise ValueError('Unknown permission')
    if permission in ADMIN_RESERVED:raise PermissionError('Reserved administrative permission')
    if allowed is not None and type(allowed) is not bool:raise ValueError('Expected true, false or default')
    row=conn.execute('SELECT role FROM users WHERE id=?',(target_id,)).fetchone()
    if not row:raise ValueError('User does not exist')
    if row[0]=='admin':raise PermissionError('Admin permissions are role-controlled')
    migrate(conn)
    previous_row=conn.execute('SELECT allowed FROM user_permission_overrides WHERE user_id=? AND permission=?',
                              (target_id,permission)).fetchone()
    previous=None if previous_row is None else bool(previous_row[0])
    if allowed is None:
        conn.execute('DELETE FROM user_permission_overrides WHERE user_id=? AND permission=?',(target_id,permission))
    else:
        conn.execute('''INSERT INTO user_permission_overrides(user_id,permission,allowed) VALUES(?,?,?)
            ON CONFLICT(user_id,permission) DO UPDATE SET allowed=excluded.allowed''',(target_id,permission,int(allowed)))
    from permission_audit import record_change
    record_change(conn,actor_id,target_id,permission,previous,allowed)
    revoke_user_sessions(conn,target_id)
    conn.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',
                 (actor_id,target_id,'permission_override_changed'))
