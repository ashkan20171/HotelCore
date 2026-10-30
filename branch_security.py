from datetime import date

def migrate(c):
    cols={r[1] for r in c.execute('PRAGMA table_info(reservations)')}
    if 'branch_id' not in cols:c.execute('ALTER TABLE reservations ADD COLUMN branch_id INTEGER REFERENCES branches(id)')
    c.execute('UPDATE reservations SET branch_id=(SELECT branch_id FROM rooms WHERE id=reservations.room_id) WHERE branch_id IS NULL')
    c.execute('CREATE INDEX IF NOT EXISTS idx_res_branch ON reservations(branch_id)')
    c.execute("CREATE TRIGGER IF NOT EXISTS branch_on_booking AFTER INSERT ON reservations WHEN NEW.branch_id IS NULL BEGIN UPDATE reservations SET branch_id=(SELECT branch_id FROM rooms WHERE id=NEW.room_id) WHERE id=NEW.id; END")
    c.execute("CREATE TRIGGER IF NOT EXISTS branch_on_room_change AFTER UPDATE OF room_id ON reservations BEGIN UPDATE reservations SET branch_id=(SELECT branch_id FROM rooms WHERE id=NEW.room_id) WHERE id=NEW.id; END")
    c.execute('CREATE TABLE IF NOT EXISTS room_branch_history(id INTEGER PRIMARY KEY,room_id INTEGER,old_branch_id INTEGER,new_branch_id INTEGER,changed_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS user_branches(user_id INTEGER REFERENCES users(id),branch_id INTEGER REFERENCES branches(id),PRIMARY KEY(user_id,branch_id))')

def transfer_room(c,room_id,branch_id,today=None):
    today=today or date.today().isoformat()
    row=c.execute('SELECT branch_id FROM rooms WHERE id=?',(room_id,)).fetchone()
    if row is None:raise ValueError('اتاق یافت نشد')
    if not c.execute('SELECT 1 FROM branches WHERE id=? AND active=1',(branch_id,)).fetchone():raise ValueError('شعبه فعال یافت نشد')
    if row[0]==branch_id:return False
    if c.execute("SELECT 1 FROM reservations WHERE room_id=? AND checkout>? AND status NOT IN ('لغو شده','خارج شده') LIMIT 1",(room_id,today)).fetchone():raise ValueError('اتاق رزرو جاری یا آینده دارد')
    c.execute('UPDATE rooms SET branch_id=? WHERE id=?',(branch_id,room_id))
    c.execute('INSERT INTO room_branch_history(room_id,old_branch_id,new_branch_id) VALUES(?,?,?)',(room_id,row[0],branch_id))
    return True

def grant_branch(c,user_id,branch_id):
    if not c.execute('SELECT 1 FROM users WHERE id=?',(user_id,)).fetchone():raise ValueError('کاربر نامعتبر')
    if not c.execute('SELECT 1 FROM branches WHERE id=? AND active=1',(branch_id,)).fetchone():raise ValueError('شعبه نامعتبر')
    c.execute('INSERT OR IGNORE INTO user_branches(user_id,branch_id) VALUES(?,?)',(user_id,branch_id))
