import sqlite3,unittest
from branch_guard import authorize_reservation,create_housekeeping,complete_housekeeping,branch_export_rows,branch_housekeeping
class GuardTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:')
  self.c.executescript('''CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER); CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER); CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT,branch_id INTEGER); CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,branch_id INTEGER,checkin TEXT,checkout TEXT,status TEXT); CREATE TABLE guests(id INTEGER,name TEXT); CREATE TABLE housekeeping(id INTEGER PRIMARY KEY,room_id INTEGER,task TEXT,status TEXT DEFAULT 'در انتظار'); INSERT INTO branches VALUES(1,'A',1),(2,'B',1); INSERT INTO user_branches VALUES(5,1); INSERT INTO rooms VALUES(10,'101',1),(20,'201',2); INSERT INTO guests VALUES(1,'Ali'); INSERT INTO reservations VALUES(1,10,1,1,'2026-10-01','2026-10-02','رزرو شده'),(2,20,1,2,'2026-10-01','2026-10-02','رزرو شده');''')
 def tearDown(self):self.c.close()
 def test_invoice_cross_branch_denied(self):
  with self.assertRaises(PermissionError):authorize_reservation(self.c,5,'staff',1,2)
 def test_export_only_own_branch(self):self.assertEqual([r[0] for r in branch_export_rows(self.c,5,'staff',1)],[1])
 def test_housekeeping_cross_branch_denied(self):
  with self.assertRaises(PermissionError):create_housekeeping(self.c,5,'staff',1,20,'نظافت')
 def test_housekeeping_completion_scoped(self):
  tid=create_housekeeping(self.c,5,'staff',1,10,'نظافت');complete_housekeeping(self.c,5,'staff',1,tid)
  self.assertEqual(branch_housekeeping(self.c,5,'staff',1)[0][3],'تکمیل شده')
 def test_no_access_to_other_branch(self):
  with self.assertRaises(PermissionError):branch_export_rows(self.c,5,'staff',2)
