"""Transaction-scoped checks for privileged user-management actions."""
from __future__ import annotations
from operation_guard import authorize_action
from user_access_management import set_account_active,set_account_role,reset_account_password
from security_sessions import revoke_user_sessions

ADMIN_ACTIONS={
    'account.toggle':'users.create',
    'account.role':'users.create',
    'account.password':'users.create',
    'session.revoke':'users.create',
}

def execute_admin_action(conn, actor_id, token, action, target_id, *, value=None, confirmation=None):
    """Authorize and mutate within the caller's SQLite transaction.

    The caller must commit after this returns. Unknown actions fail closed.
    """
    if action not in ADMIN_ACTIONS:
        raise ValueError('Unsupported administrative action')
    authorize_action(conn,actor_id,token,ADMIN_ACTIONS[action])
    if action=='account.toggle':
        if not isinstance(value,bool):raise ValueError('Active state must be boolean')
        set_account_active(conn,actor_id,target_id,value)
    elif action=='account.role':
        set_account_role(conn,actor_id,target_id,value)
    elif action=='account.password':
        reset_account_password(conn,actor_id,target_id,value,confirmation)
    else:
        # Revoke sessions of a target only when it exists.
        if not conn.execute('SELECT 1 FROM users WHERE id=?',(target_id,)).fetchone():
            raise ValueError('User does not exist')
        revoke_user_sessions(conn,target_id)
        conn.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',
                     (actor_id,target_id,'sessions_revoked'))
    return True
