"""Branch-authorized reservation and payment operations.
All checks happen within the same database transaction as writes.
"""
from branch_access import require_branch

def require_room(conn, user_id, role, branch_id, room_id):
    require_branch(conn,user_id,role,branch_id)
    row=conn.execute("SELECT branch_id FROM rooms WHERE id=? AND status='فعال'",(room_id,)).fetchone()
    if not row or row[0]!=branch_id: raise PermissionError('اتاق در شعبه مجاز نیست')

def require_reservation(conn,user_id,role,branch_id,reservation_id):
    require_branch(conn,user_id,role,branch_id)
    row=conn.execute('SELECT branch_id,status FROM reservations WHERE id=?',(reservation_id,)).fetchone()
    if not row or row[0]!=branch_id: raise PermissionError('رزرو در شعبه مجاز نیست')
    return row[1]

def record_payment(conn,user_id,role,branch_id,reservation_id,amount,method):
    require_reservation(conn,user_id,role,branch_id,reservation_id)
    if not isinstance(amount,int) or amount<=0: raise ValueError('مبلغ نامعتبر')
    if method not in ('کارتخوان','نقدی','انتقال بانکی'): raise ValueError('روش پرداخت نامعتبر')
    return conn.execute('INSERT INTO payments(reservation_id,amount,method) VALUES(?,?,?)',(reservation_id,amount,method)).lastrowid

def change_reservation_status(conn,user_id,role,branch_id,reservation_id,new_status):
    old=require_reservation(conn,user_id,role,branch_id,reservation_id)
    transitions={'رزرو شده':('پذیرش شده','لغو شده'),'پذیرش شده':('خارج شده',)}
    if new_status not in transitions.get(old,()):raise ValueError('تغییر وضعیت مجاز نیست')
    conn.execute('UPDATE reservations SET status=? WHERE id=? AND branch_id=?',(new_status,reservation_id,branch_id))

def grant_user_branch(conn,actor_id,actor_role,user_id,branch_id):
    if actor_role!='admin':raise PermissionError('فقط مدیر مجاز است')
    require_branch(conn,actor_id,actor_role,branch_id)
    if not conn.execute('SELECT 1 FROM users WHERE id=?',(user_id,)).fetchone():raise ValueError('کاربر وجود ندارد')
    conn.execute('INSERT OR IGNORE INTO user_branches(user_id,branch_id) VALUES(?,?)',(user_id,branch_id))

def revoke_user_branch(conn,actor_id,actor_role,user_id,branch_id):
    if actor_role!='admin':raise PermissionError('فقط مدیر مجاز است')
    require_branch(conn,actor_id,actor_role,branch_id)
    conn.execute('DELETE FROM user_branches WHERE user_id=? AND branch_id=?',(user_id,branch_id))
