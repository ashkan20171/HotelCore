"""Report Center: admin-only audit trail for system-health exports.

Only minimal metadata is stored. Never persist session tokens, patient/guest data,
or absolute filesystem paths. A failed audit write must not change export outcome.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from user_access_management import _actor

STATES = frozenset({'success', 'failed', 'cancelled'})
FORMATS = frozenset({'pdf', 'xlsx'})

def migrate(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS health_report_exports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        actor_id INTEGER NOT NULL,
        format TEXT NOT NULL CHECK(format IN ('pdf','xlsx')),
        status TEXT NOT NULL CHECK(status IN ('success','failed','cancelled')),
        filename TEXT NOT NULL,
        record_count INTEGER NOT NULL DEFAULT 0,
        error_code TEXT NOT NULL DEFAULT ''
    )""")
    conn.execute('CREATE INDEX IF NOT EXISTS ix_health_report_exports_created ON health_report_exports(created_at DESC)')

def record_export(conn, actor_id, *, fmt, status, filename, record_count=0, error_code=''):
    _actor(conn, actor_id)
    if fmt not in FORMATS or status not in STATES: raise ValueError('Invalid export format/status')
    if type(record_count) is not int or record_count < 0: raise ValueError('Invalid record count')
    basename = Path(filename).name
    if not basename or basename in ('.', '..') or len(basename)>180: raise ValueError('Invalid filename')
    if error_code not in ('', 'permission', 'database', 'filesystem', 'cancelled', 'unexpected'):
        raise ValueError('Invalid error code')
    migrate(conn)
    conn.execute('INSERT INTO health_report_exports(created_at,actor_id,format,status,filename,record_count,error_code) VALUES(?,?,?,?,?,?,?)',
        (datetime.now(timezone.utc).isoformat(),actor_id,fmt,status,basename,record_count,error_code))
    conn.commit()

def list_exports(conn, actor_id, *, status='all', fmt='all', search='', limit=100):
    _actor(conn,actor_id)
    if status not in STATES | {'all'} or fmt not in FORMATS | {'all'}: raise ValueError('Invalid filter')
    if type(limit) is not int or not 1 <= limit <= 500: raise ValueError('Invalid limit')
    if not isinstance(search,str) or len(search)>100: raise ValueError('Invalid search')
    migrate(conn)
    sql='SELECT created_at,format,status,filename,record_count,error_code FROM health_report_exports WHERE 1=1'
    args=[]
    if status!='all':sql+=' AND status=?';args.append(status)
    if fmt!='all':sql+=' AND format=?';args.append(fmt)
    if search:
        sql+=" AND instr(lower(filename), lower(?)) > 0";args.append(search)
    sql+=' ORDER BY id DESC LIMIT ?';args.append(limit)
    return conn.execute(sql,args).fetchall()
