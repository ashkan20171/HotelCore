"""Permission-gated security overview; no guest data or credential disclosure."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from user_access_management import _actor

ADMIN_ONLY=frozenset({'users.manage','security.view','security.revoke','finance.manage','branches.manage'})
ROLE_PERMISSIONS={
    'admin':ADMIN_ONLY | frozenset({'reservations.view','reservations.manage','guests.view','housekeeping.manage'}),
    'reception':frozenset({'reservations.view','reservations.manage','guests.view','housekeeping.manage'}),
}

def require_permission(conn,user_id,permission):
    if permission not in set().union(*ROLE_PERMISSIONS.values()):
        raise ValueError('Unknown permission')
    from permission_policy import require_user_permission
    return require_user_permission(conn,user_id,permission)

def security_summary(conn,actor_id,*,days=7,now=None):
    """Aggregate login activity in UTC; recent events are bounded and admin-only."""
    require_permission(conn,actor_id,'security.view')
    if not isinstance(days,int) or isinstance(days,bool) or not 1<=days<=90:
        raise ValueError('days must be 1–90')
    instant=now or datetime.now(timezone.utc)
    if instant.tzinfo is None:raise ValueError('now must be timezone-aware')
    instant=instant.astimezone(timezone.utc)
    start=(instant-timedelta(days=days)).isoformat()
    end=instant.isoformat()
    results=dict.fromkeys(('success','failure','locked'),0)
    for outcome,count in conn.execute("""SELECT outcome,COUNT(*) FROM login_events
        WHERE occurred_at>=? AND occurred_at<=? GROUP BY outcome""",(start,end)):
        if outcome in results:results[outcome]=count
    active_sessions=conn.execute("""SELECT COUNT(*) FROM user_sessions s JOIN users u ON u.id=s.user_id
        WHERE s.revoked_at IS NULL AND s.expires_at>? AND u.active=1""",(end,)).fetchone()[0]
    disabled=conn.execute('SELECT COUNT(*) FROM users WHERE active=0').fetchone()[0]
    total=conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    return {'days':days,'success':results['success'],'failure':results['failure'],
            'locked':results['locked'],'active_sessions':active_sessions,
            'disabled_accounts':disabled,'total_accounts':total}

def recent_security_changes(conn,actor_id,limit=30):
    require_permission(conn,actor_id,'security.view')
    if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=100:
        raise ValueError('limit must be 1–100')
    return conn.execute("""SELECT e.created_at,COALESCE(a.username,'—'),
        COALESCE(t.username,'—'),e.event FROM security_events e
        LEFT JOIN users a ON a.id=e.actor_id LEFT JOIN users t ON t.id=e.target_id
        ORDER BY e.id DESC LIMIT ?""",(limit,)).fetchall()
