import sqlite3, unittest
from branches import migrate_branches,add_branch,assign_room
from branch_reports import branch_summary,branch_reservations
from branch_security import migrate

class BranchReportsTest(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT,kind TEXT,rate INTEGER,status TEXT DEFAULT 'فعال');
  CREATE TABLE guests(id INTEGER PRIMARY KEY,name TEXT,phone TEXT);
  CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,guest_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);
  CREATE TABLE payments(id INTEGER PRIMARY KEY,reservation_id INTEGER,amount INTEGER,created_at TEXT);
  CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT);""")
  migrate_branches(self.db)
  self.db.execute("INSERT INTO rooms(id,number) VALUES(1,'101'),(2,'201')")
  self.db.execute("INSERT INTO guests(id,name) VALUES(1,'مهمان')")
  self.bid=add_branch(self.db,'شعبه دوم')
  assign_room(self.db,2,self.bid)
  migrate(self.db)
  self.db.execute("INSERT INTO reservations(id,room_id,guest_id,checkin,checkout,status) VALUES(1,1,1,'2026-10-01','2026-10-04','رزرو شده')")
  self.db.execute("INSERT INTO reservations(id,room_id,guest_id,checkin,checkout,status) VALUES(2,2,1,'2026-10-02','2026-10-05','رزرو شده')")
  self.db.execute("INSERT INTO payments VALUES(1,1,100,'2026-10-02')")
  self.db.execute("INSERT INTO payments VALUES(2,2,200,'2026-10-03')")
 def tearDown(self):self.db.close()
 def test_branch_isolation(self):
  a=branch_summary(self.db,1,'2026-10-01','2026-10-06')
  b=branch_summary(self.db,self.bid,'2026-10-01','2026-10-06')
  self.assertEqual((a['payments'],b['payments']),(100,200))
  self.assertEqual(len(branch_reservations(self.db,self.bid,'2026-10-01','2026-10-06')),1)
 def test_night_intersection(self):
  self.assertEqual(branch_summary(self.db,self.bid,'2026-10-03','2026-10-04')['occupied_nights'],1)
 def test_invalid_range(self):
  with self.assertRaises(ValueError):branch_summary(self.db,1,'2026-10-05','2026-10-04')
 def test_unknown_branch(self):
  with self.assertRaises(ValueError):branch_summary(self.db,999,'2026-10-01','2026-10-05')
