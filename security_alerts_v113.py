"""Auditable security alert thresholds and snapshots. Active administrators only."""
from datetime import datetime, timezone
from user_access_management import _actor
from security_dashboard_v112 import compare_windows

SEVERITIES=('high','review','normal')

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS security_alert_settings (
        id INTEGER PRIMARY KEY CHECK(id=1), threshold INTEGER NOT NULL DEFAULT 5
        CHECK(threshold BETWEEN 1 AND 100), updated_by INTEGER,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS security_alert_history (
        id INTEGER PRIMARY KEY, actor_id INTEGER NOT NULL, username_filter TEXT,
        days INTEGER NOT NULL, severity TEXT NOT NULL, failed_attempts INTEGER NOT NULL,
        previous_attempts INTEGER NOT NULL, threshold INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute('CREATE INDEX IF NOT EXISTS idx_security_alert_history_date ON security_alert_history(id DESC)')
    conn.execute('INSERT OR IGNORE INTO security_alert_settings(id,threshold) VALUES(1,5)')

def get_threshold(conn,actor_id):
    _actor(conn,actor_id)
    migrate(conn)
    return conn.execute('SELECT threshold FROM security_alert_settings WHERE id=1').fetchone()[0]

def set_threshold(conn,actor_id,threshold):
    _actor(conn,actor_id)
    if type(threshold) is not int or not 1 <= threshold <= 100:
        raise ValueError('Threshold must be between 1 and 100')
    migrate(conn)
    conn.execute('UPDATE security_alert_settings SET threshold=?,updated_by=?,updated_at=CURRENT_TIMESTAMP WHERE id=1',(threshold,actor_id))
    return threshold

def evaluate_and_record(conn,actor_id,*,days=7,username=None,now=None):
    _actor(conn,actor_id)
    threshold=get_threshold(conn,actor_id)
    result=compare_windows(conn,actor_id,days=days,username=username,now=now,alert_threshold=threshold)
    current=result['current']['totals']; previous=result['previous']['totals']
    bad=current['failure']+current['locked']; prior=previous['failure']+previous['locked']
    severity=result['alert']
    # Only persist actionable signals, and avoid duplicate snapshots of the same state.
    if severity != 'normal':
        last=conn.execute("""SELECT severity,failed_attempts,previous_attempts,threshold FROM security_alert_history
            WHERE username_filter IS ? AND days=? ORDER BY id DESC LIMIT 1""",(username,days)).fetchone()
        state=(severity,bad,prior,threshold)
        if last != state:
            conn.execute("""INSERT INTO security_alert_history
                (actor_id,username_filter,days,severity,failed_attempts,previous_attempts,threshold)
                VALUES(?,?,?,?,?,?,?)""",(actor_id,username,days,*state))
    return result

def alert_history(conn,actor_id,*,severity=None,limit=100):
    _actor(conn,actor_id)
    if severity is not None and severity not in ('high','review'):
        raise ValueError('Unsupported severity')
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('Invalid limit')
    migrate(conn)
    sql="""SELECT created_at,COALESCE(username_filter,'*'),days,severity,failed_attempts,previous_attempts,threshold
           FROM security_alert_history"""
    if severity is not None:
        return conn.execute(sql+' WHERE severity=? ORDER BY id DESC LIMIT ?',(severity,limit)).fetchall()
    return conn.execute(sql+' ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
