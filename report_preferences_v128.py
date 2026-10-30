"""Admin-only persistent system health report preferences and named presets."""
import re
from user_access_management import _actor

_NAME = re.compile(r"^[\w -]{1,40}$", re.UNICODE)

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS health_report_presets (
        actor_id INTEGER NOT NULL, name TEXT NOT NULL,
        days INTEGER NOT NULL CHECK(days BETWEEN 1 AND 90),
        threshold INTEGER NOT NULL CHECK(threshold BETWEEN 0 AND 100),
        PRIMARY KEY(actor_id, name))""")

def validate(name, days, threshold):
    if not isinstance(name,str) or not _NAME.fullmatch(name) or name.strip()!=name:
        raise ValueError('Preset name must be 1-40 letters, digits, spaces, - or _')
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('Days must be 1-90')
    if type(threshold) is not int or not 0 <= threshold <= 100:
        raise ValueError('Threshold must be 0-100')

def save_preset(conn, actor_id, name, days, threshold):
    _actor(conn, actor_id)
    validate(name,days,threshold)
    migrate(conn)
    if conn.execute('SELECT COUNT(*) FROM health_report_presets WHERE actor_id=?',(actor_id,)).fetchone()[0] >= 20:
        if not conn.execute('SELECT 1 FROM health_report_presets WHERE actor_id=? AND name=?',(actor_id,name)).fetchone():
            raise ValueError('Maximum 20 presets per administrator')
    conn.execute('INSERT INTO health_report_presets(actor_id,name,days,threshold) VALUES(?,?,?,?) '
                 'ON CONFLICT(actor_id,name) DO UPDATE SET days=excluded.days,threshold=excluded.threshold',
                 (actor_id,name,days,threshold))
    conn.commit()

def list_presets(conn,actor_id):
    _actor(conn,actor_id)
    migrate(conn)
    return conn.execute('SELECT name,days,threshold FROM health_report_presets WHERE actor_id=? ORDER BY name', (actor_id,)).fetchall()

def delete_preset(conn,actor_id,name):
    _actor(conn,actor_id)
    if not isinstance(name,str) or not _NAME.fullmatch(name):raise ValueError('Invalid name')
    migrate(conn)
    cursor=conn.execute('DELETE FROM health_report_presets WHERE actor_id=? AND name=?',(actor_id,name))
    conn.commit()
    return cursor.rowcount > 0
