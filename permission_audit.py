"""Permission change history with administrator-only reads and CSV-safe exports."""
import csv
from user_access_management import _actor

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS permission_audit (
        id INTEGER PRIMARY KEY,
        actor_id INTEGER,
        target_id INTEGER NOT NULL,
        permission TEXT NOT NULL,
        previous_value TEXT NOT NULL,
        new_value TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_permission_audit_target ON permission_audit(target_id,id DESC)")

def record_change(conn, actor_id, target_id, permission, previous, new):
    migrate(conn)
    conn.execute("""INSERT INTO permission_audit
        (actor_id,target_id,permission,previous_value,new_value)
        VALUES(?,?,?,?,?)""",
        (actor_id,target_id,permission,_value(previous),_value(new)))

def _value(value):
    if value is None: return 'default'
    if value is True or value == 1: return 'allow'
    if value is False or value == 0: return 'deny'
    raise ValueError('Invalid permission audit value')

def recent_changes(conn, actor_id, *, target_id=None, limit=100):
    _actor(conn,actor_id)
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('Limit must be 1..500')
    migrate(conn)
    if target_id is None:
        return conn.execute("""SELECT a.created_at,COALESCE(actor.username,'—'),
            COALESCE(target.username,'—'),a.permission,a.previous_value,a.new_value
            FROM permission_audit a
            LEFT JOIN users actor ON actor.id=a.actor_id
            LEFT JOIN users target ON target.id=a.target_id
            ORDER BY a.id DESC LIMIT ?""",(limit,)).fetchall()
    if not conn.execute('SELECT 1 FROM users WHERE id=?',(target_id,)).fetchone():
        raise ValueError('User does not exist')
    return conn.execute("""SELECT a.created_at,COALESCE(actor.username,'—'),
        COALESCE(target.username,'—'),a.permission,a.previous_value,a.new_value
        FROM permission_audit a
        LEFT JOIN users actor ON actor.id=a.actor_id
        LEFT JOIN users target ON target.id=a.target_id
        WHERE a.target_id=? ORDER BY a.id DESC LIMIT ?""",(target_id,limit)).fetchall()

def export_changes_csv(path, rows):
    fields=('created_at','actor','target','permission','previous_value','new_value')
    def safe(value):
        value='' if value is None else str(value)
        return "'"+value if value.lstrip().startswith(('=','+','-','@','\\t','\\r','\\n')) else value
    with open(path,'w',encoding='utf-8-sig',newline='') as handle:
        writer=csv.writer(handle)
        writer.writerow(fields)
        writer.writerows([safe(value) for value in row] for row in rows)
    return len(rows)
