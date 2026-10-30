import sqlite3,unittest
from branches import migrate_branches
from branch_security import migrate,transfer_room,grant_branch
class BranchTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:')
  self.c.executescript("CREATE TABLE rooms(id INTEGER PRIMARY KEY,number TEXT,branch_id INTEGER);CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,checkin TEXT,checkout TEXT,status TEXT);CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT);INSERT INTO rooms VALUES(1,'101',1);INSERT INTO users VALUES(1,'a','reception');")
  migrate_branches(self.c);self.c.execute("INSERT INTO branches(id,name) VALUES(2,'second')");migrate(self.c)
 def tearDown(self):self.c.close()
 def test_transfer(self):
  self.assertTrue(transfer_room(self.c,1,2,'2026-01-01'))
  self.assertEqual(self.c.execute('SELECT old_branch_id,new_branch_id FROM room_branch_history').fetchone(),(1,2))
 def test_future_booking_blocked(self):
  self.c.execute("INSERT INTO reservations(id,room_id,checkin,checkout,status) VALUES(1,1,'2026-01-01','2027-01-01','رزرو شده')")
  with self.assertRaises(ValueError):transfer_room(self.c,1,2,'2026-02-01')
 def test_historical_snapshot(self):
  self.c.execute("INSERT INTO reservations(id,room_id,checkin,checkout,status) VALUES(1,1,'2025-01-01','2025-01-03','خارج شده')")
  transfer_room(self.c,1,2,'2026-01-01')
  self.assertEqual(self.c.execute('SELECT branch_id FROM reservations').fetchone()[0],1)
 def test_user_grant(self):
  grant_branch(self.c,1,2)
  self.assertEqual(self.c.execute('SELECT branch_id FROM user_branches').fetchone()[0],2)
 def test_invalid_grant(self):
  with self.assertRaises(ValueError):grant_branch(self.c,1,99)
