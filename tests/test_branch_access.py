import unittest, sqlite3
from branch_access import allowed_branches,require_branch,scoped_reservations,scoped_payments,branch_dashboard
class BranchAccessTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:')
  self.c.executescript('''CREATE TABLE branches(id INTEGER,name TEXT,active INTEGER);
  CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER);
  CREATE TABLE rooms(id INTEGER,number TEXT,branch_id INTEGER,status TEXT);
  CREATE TABLE guests(id INTEGER,name TEXT);
  CREATE TABLE reservations(id INTEGER,room_id INTEGER,guest_id INTEGER,branch_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
  CREATE TABLE payments(id INTEGER,reservation_id INTEGER,amount INTEGER,method TEXT,created_at TEXT);
  INSERT INTO branches VALUES(1,'الف',1),(2,'ب',1),(3,'غیرفعال',0);
  INSERT INTO user_branches VALUES(7,1);
  INSERT INTO rooms VALUES(1,'101',1,'فعال'),(2,'201',2,'فعال');
  INSERT INTO guests VALUES(1,'مهمان');
  INSERT INTO reservations VALUES(1,1,1,1,'2026-10-01','2026-10-02','رزرو شده'),(2,2,1,2,'2026-10-01','2026-10-02','رزرو شده');
  INSERT INTO payments VALUES(1,1,100,'نقدی','2026-10-01'),(2,2,200,'نقدی','2026-10-01');''')
 def tearDown(self):self.c.close()
 def test_allowed(self):self.assertEqual(allowed_branches(self.c,7,'reception'),[(1,'الف')])
 def test_denied(self):
  with self.assertRaises(PermissionError):require_branch(self.c,7,'reception',2)
 def test_inactive_denied_admin(self):
  with self.assertRaises(PermissionError):require_branch(self.c,1,'admin',3)
 def test_scoped_reservations(self):self.assertEqual([r[0] for r in scoped_reservations(self.c,7,'reception',1)],[1])
 def test_scoped_payments(self):self.assertEqual([r[0] for r in scoped_payments(self.c,7,'reception',1)],[1])
 def test_summary(self):self.assertEqual(branch_dashboard(self.c,7,'reception',1),{'rooms':1,'reservations':1,'payments':100})
