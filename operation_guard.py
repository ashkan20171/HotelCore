"""Fail-closed authorization for sensitive UI actions and service entry points."""
from security_overview import require_permission
from security_sessions import validate_session

ACTION_PERMISSIONS = {
    'security.view': 'security.view',
    'users.create': 'users.manage',
    'finance.export': 'finance.manage',
    'finance.expense': 'finance.manage',
    'finance.inventory': 'finance.manage',
    'staff.manage': 'users.manage',
    'reservations.create': 'reservations.manage',
    'reservations.update': 'reservations.manage',
    'reservations.payment': 'reservations.manage',
    'reservations.services': 'reservations.manage',
    'reservations.invoice': 'reservations.view',
}

def authorize_action(conn, user_id, token, action):
    """Validate both live session and current database role before sensitive action."""
    if action not in ACTION_PERMISSIONS:
        raise ValueError('Unknown operation')
    if not token or not validate_session(conn, token):
        raise PermissionError('Session expired or revoked')
    require_permission(conn, user_id, ACTION_PERMISSIONS[action])
    return True
