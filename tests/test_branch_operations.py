import sqlite3, unittest
from branch_operations import require_room, record_payment, change_reservation_status, grant_user_branch, revoke_user_branch
from branch_access import allowed_branches

class BranchOperationsTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript('''CREATE TABLE branches(id INTEGER PRIMARY KEY,name TEXT,active INTEGER); CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT); CREATE TABLE user_branches(user_id INTEGER,branch_id INTEGER,PRIMARY KEY(user_id,branch_id)); CREATE TABLE rooms(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT); CREATE TABLE reservations(id INTEGER PRIMARY KEY,branch_id INTEGER,status TEXT); CREATE TABLE payments(id INTEGER PRIMARY KEY,reservation_id INTEGER,amount INTEGER,method TEXT); INSERT INTO branches VALUES(1,'A',1),(2,'B',1); INSERT INTO users VALUES(1,'admin'),(2,'clerk'); INSERT INTO user_branches VALUES(2,1); INSERT INTO rooms VALUES(11,1,'فعال'),(22,2,'فعال'); INSERT INTO reservations VALUES(101,1,'رزرو شده'),(202,2,'رزرو شده');''')
 def tearDown(self):self.db.close()
 def test_room_isolation(self):
  require_room(self.db,2,'reception',1,11)
  with self.assertRaises(PermissionError):require_room(self.db,2,'reception',1,22)
 def test_payment_isolation(self):
  with self.assertRaises(PermissionError):record_payment(self.db,2,'reception',1,202,100,'نقدی')
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM payments').fetchone()[0],0)
  record_payment(self.db,2,'reception',1,101,100,'نقدی')
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM payments').fetchone()[0],1)
 def test_status_isolation(self):
  with self.assertRaises(PermissionError):change_reservation_status(self.db,2,'reception',1,202,'پذیرش شده')
  change_reservation_status(self.db,2,'reception',1,101,'پذیرش شده')
  self.assertEqual(self.db.execute('SELECT status FROM reservations WHERE id=101').fetchone()[0],'پذیرش شده')
 def test_grants(self):
  with self.assertRaises(PermissionError):grant_user_branch(self.db,2,'reception',2,2)
  grant_user_branch(self.db,1,'admin',2,2)
  self.assertEqual(len(allowed_branches(self.db,2,'reception')),2)
  revoke_user_branch(self.db,1,'admin',2,2)
  self.assertEqual(len(allowed_branches(self.db,2,'reception')),1)
if __name__=='__main__':unittest.main()
