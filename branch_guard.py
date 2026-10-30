"""Branch authorization helpers for previously unscoped operations."""
from branch_access import require_branch

def authorize_reservation(conn, user_id, role, branch_id, reservation_id):
    require_branch(conn,user_id,role,branch_id)
    row=conn.execute('SELECT branch_id FROM reservations WHERE id=?',(reservation_id,)).fetchone()
    if row is None or row[0]!=branch_id:
        raise PermissionError('رزرو در شعبه مجاز نیست')
    return reservation_id

def authorize_room(conn,user_id,role,branch_id,room_id):
    require_branch(conn,user_id,role,branch_id)
    row=conn.execute('SELECT branch_id FROM rooms WHERE id=?',(room_id,)).fetchone()
    if row is None or row[0]!=branch_id:
        raise PermissionError('اتاق در شعبه مجاز نیست')
    return room_id

def create_housekeeping(conn,user_id,role,branch_id,room_id,task):
    authorize_room(conn,user_id,role,branch_id,room_id)
    if not isinstance(task,str) or not task.strip():raise ValueError('وظیفه نامعتبر است')
    return conn.execute('INSERT INTO housekeeping(room_id,task) VALUES(?,?)',(room_id,task.strip())).lastrowid

def complete_housekeeping(conn,user_id,role,branch_id,task_id):
    require_branch(conn,user_id,role,branch_id)
    row=conn.execute('SELECT rm.branch_id FROM housekeeping h JOIN rooms rm ON rm.id=h.room_id WHERE h.id=?',(task_id,)).fetchone()
    if row is None or row[0]!=branch_id:raise PermissionError('وظیفه در شعبه مجاز نیست')
    conn.execute("UPDATE housekeeping SET status='تکمیل شده' WHERE id=?",(task_id,))

def branch_housekeeping(conn,user_id,role,branch_id):
    require_branch(conn,user_id,role,branch_id)
    return conn.execute('SELECT h.id,rm.number,h.task,h.status FROM housekeeping h JOIN rooms rm ON rm.id=h.room_id WHERE rm.branch_id=? ORDER BY h.id DESC',(branch_id,)).fetchall()

def branch_export_rows(conn,user_id,role,branch_id):
    require_branch(conn,user_id,role,branch_id)
    return conn.execute('SELECT r.id,ro.number,g.name,r.checkin,r.checkout,r.status FROM reservations r JOIN rooms ro ON ro.id=r.room_id JOIN guests g ON g.id=r.guest_id WHERE r.branch_id=? ORDER BY r.id',(branch_id,)).fetchall()
