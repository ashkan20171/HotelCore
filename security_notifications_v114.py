"""Administrator-only, persistent inbox for security alert snapshots.

Notifications are synchronized from alert history; this is not background monitoring.
"""
from datetime import datetime, timezone
from user_access_management import _actor


def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS security_notifications (
        id INTEGER PRIMARY KEY,
        alert_id INTEGER NOT NULL UNIQUE,
        is_read INTEGER NOT NULL DEFAULT 0 CHECK(is_read IN (0,1)),
        acknowledged_by INTEGER,
        acknowledged_at TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(alert_id) REFERENCES security_alert_history(id))''')
    columns={row[1] for row in conn.execute('PRAGMA table_info(security_notifications)')}
    if 'archived_at' not in columns:
        conn.execute('ALTER TABLE security_notifications ADD COLUMN archived_at TEXT')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_security_notifications_unread ON security_notifications(is_read,id DESC)')


def sync_alerts(conn, actor_id):
    _actor(conn,actor_id)
    from security_alerts_v113 import migrate as migrate_alerts
    migrate_alerts(conn)
    migrate(conn)
    conn.execute('''INSERT OR IGNORE INTO security_notifications(alert_id)
                    SELECT id FROM security_alert_history WHERE severity IN ('high','review')''')
    return unread_count(conn,actor_id)


def unread_count(conn,actor_id):
    _actor(conn,actor_id)
    migrate(conn)
    return conn.execute('SELECT COUNT(*) FROM security_notifications WHERE is_read=0 AND archived_at IS NULL').fetchone()[0]


def inbox(conn,actor_id,*,status='all',severity=None,limit=100):
    _actor(conn,actor_id)
    if status not in ('all','unread','read','acknowledged','archived'):
        raise ValueError('Invalid notification status')
    if severity not in (None,'high','review'):
        raise ValueError('Invalid severity')
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('Invalid limit')
    migrate(conn)
    where=['n.archived_at IS NOT NULL' if status=='archived' else 'n.archived_at IS NULL'];params=[]
    if status=='unread':where.append('n.is_read=0')
    elif status=='read':where.append('n.is_read=1')
    elif status=='acknowledged':where.append('n.acknowledged_at IS NOT NULL')
    if severity:
        where.append('a.severity=?');params.append(severity)
    sql='''SELECT n.id,n.created_at,COALESCE(a.username_filter,'*'),a.severity,
             a.failed_attempts,n.is_read,n.acknowledged_at
             FROM security_notifications n JOIN security_alert_history a ON a.id=n.alert_id'''
    if where:sql+=' WHERE '+' AND '.join(where)
    sql+=' ORDER BY n.id DESC LIMIT ?';params.append(limit)
    return conn.execute(sql,params).fetchall()


def mark_read(conn,actor_id,notification_id):
    _actor(conn,actor_id)
    if type(notification_id) is not int or notification_id < 1:raise ValueError('Invalid notification id')
    migrate(conn)
    cur=conn.execute('UPDATE security_notifications SET is_read=1 WHERE id=? AND archived_at IS NULL',(notification_id,))
    if not cur.rowcount:raise ValueError('Notification not found')
    return True


def acknowledge(conn,actor_id,notification_id):
    _actor(conn,actor_id)
    if type(notification_id) is not int or notification_id < 1:raise ValueError('Invalid notification id')
    migrate(conn)
    cur=conn.execute('''UPDATE security_notifications SET is_read=1,
        acknowledged_by=COALESCE(acknowledged_by,?),
        acknowledged_at=COALESCE(acknowledged_at,?) WHERE id=? AND archived_at IS NULL''',
        (actor_id,datetime.now(timezone.utc).isoformat(timespec='seconds'),notification_id))
    if not cur.rowcount:raise ValueError('Notification not found')
    return True


def archive(conn, actor_id, notification_id):
    """Archive an alert without deleting its audit record."""
    _actor(conn, actor_id)
    if type(notification_id) is not int or notification_id < 1:
        raise ValueError('Invalid notification id')
    migrate(conn)
    timestamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
    result=conn.execute('UPDATE security_notifications SET archived_at=?, is_read=1 WHERE id=? AND archived_at IS NULL', (timestamp,notification_id))
    if not result.rowcount:
        raise ValueError('Active notification not found')
    return True

def restore(conn, actor_id, notification_id):
    """Restore an archived alert as already read."""
    _actor(conn, actor_id)
    if type(notification_id) is not int or notification_id < 1:
        raise ValueError('Invalid notification id')
    migrate(conn)
    result=conn.execute('UPDATE security_notifications SET archived_at=NULL, is_read=1 WHERE id=? AND archived_at IS NOT NULL', (notification_id,))
    if not result.rowcount:
        raise ValueError('Archived notification not found')
    return True
