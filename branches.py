"""Incremental branch registry and legacy-room migration."""
import sqlite3

def migrate_branches(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
        city TEXT NOT NULL DEFAULT '', address TEXT NOT NULL DEFAULT '',
        phone TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
    )""")
    conn.execute("INSERT OR IGNORE INTO branches(id,name,city) VALUES(1,'شعبه مرکزی','')")
    columns={r[1] for r in conn.execute('PRAGMA table_info(rooms)')}
    if 'branch_id' not in columns:
        conn.execute('ALTER TABLE rooms ADD COLUMN branch_id INTEGER REFERENCES branches(id) DEFAULT 1')
    conn.execute('UPDATE rooms SET branch_id=1 WHERE branch_id IS NULL')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_rooms_branch ON rooms(branch_id)')

def add_branch(conn,name,city='',address='',phone=''):
    name=name.strip()
    if not name: raise ValueError('نام شعبه الزامی است')
    return conn.execute('INSERT INTO branches(name,city,address,phone) VALUES(?,?,?,?)',
                        (name,city.strip(),address.strip(),phone.strip())).lastrowid

def assign_room(conn,room_id,branch_id):
    if not conn.execute('SELECT 1 FROM rooms WHERE id=?',(room_id,)).fetchone():
        raise ValueError('اتاق یافت نشد')
    if not conn.execute('SELECT 1 FROM branches WHERE id=? AND active=1',(branch_id,)).fetchone():
        raise ValueError('شعبه فعال یافت نشد')
    conn.execute('UPDATE rooms SET branch_id=? WHERE id=?',(branch_id,room_id))
