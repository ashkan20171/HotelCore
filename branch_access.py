"""Branch access policy. Every write path must separately enforce require_branch."""

def allowed_branches(conn, user_id, role):
    if user_id is None:
        return []
    if role == 'admin':
        return conn.execute('SELECT id,name FROM branches WHERE active=1 ORDER BY name').fetchall()
    return conn.execute('''SELECT b.id,b.name FROM branches b
        JOIN user_branches ub ON ub.branch_id=b.id
        WHERE ub.user_id=? AND b.active=1 ORDER BY b.name''',(user_id,)).fetchall()

def require_branch(conn,user_id,role,branch_id):
    if not isinstance(branch_id,int) or branch_id not in {bid for bid,_ in allowed_branches(conn,user_id,role)}:
        raise PermissionError('دسترسی به این شعبه مجاز نیست')
    return branch_id

def scoped_reservations(conn,user_id,role,branch_id):
    require_branch(conn,user_id,role,branch_id)
    return conn.execute('''SELECT r.id,rm.number,g.name,r.checkin,r.checkout,r.status
        FROM reservations r JOIN rooms rm ON rm.id=r.room_id
        JOIN guests g ON g.id=r.guest_id WHERE r.branch_id=? ORDER BY r.id DESC''',(branch_id,)).fetchall()

def scoped_payments(conn,user_id,role,branch_id):
    require_branch(conn,user_id,role,branch_id)
    return conn.execute('''SELECT p.id,p.reservation_id,p.amount,p.method,p.created_at
        FROM payments p JOIN reservations r ON r.id=p.reservation_id
        WHERE r.branch_id=? ORDER BY p.id DESC''',(branch_id,)).fetchall()

def branch_dashboard(conn,user_id,role,branch_id):
    require_branch(conn,user_id,role,branch_id)
    rooms=conn.execute('SELECT COUNT(*) FROM rooms WHERE branch_id=? AND status=?',(branch_id,'فعال')).fetchone()[0]
    bookings=conn.execute("SELECT COUNT(*) FROM reservations WHERE branch_id=? AND status<>'لغو شده'",(branch_id,)).fetchone()[0]
    paid=conn.execute('''SELECT COALESCE(SUM(p.amount),0) FROM payments p
        JOIN reservations r ON r.id=p.reservation_id WHERE r.branch_id=?''',(branch_id,)).fetchone()[0]
    return {'rooms':rooms,'reservations':bookings,'payments':paid}
