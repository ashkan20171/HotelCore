import sqlite3
import unittest
from user_access_management import migrate,list_accounts,set_account_active,set_account_role,reset_account_password

class UserAccessTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT,salt TEXT,role TEXT)')
  self.db.executemany('INSERT INTO users(id,username,password_hash,salt,role) VALUES(?,?,?,?,?)',[
   (1,'boss','hash','salt','admin'),(2,'clerk','hash','salt','reception'),(3,'second','hash','salt','admin')])
  migrate(self.db)
 def test_migration_idempotent(self):
  migrate(self.db);self.assertEqual(len(list_accounts(self.db,1)),3)
 def test_disable_and_enable(self):
  set_account_active(self.db,1,2,False)
  self.assertEqual(self.db.execute('SELECT active FROM users WHERE id=2').fetchone()[0],0)
  set_account_active(self.db,1,2,True)
  self.assertEqual(self.db.execute('SELECT active FROM users WHERE id=2').fetchone()[0],1)
 def test_no_self_disable(self):
  with self.assertRaises(ValueError):set_account_active(self.db,1,1,False)
 def test_no_last_admin_disable(self):
  set_account_active(self.db,1,3,False)
  from user_access_management import _protect_last_admin
  with self.assertRaises(ValueError):_protect_last_admin(self.db,1)
 def test_role_change(self):
  set_account_role(self.db,1,2,'admin')
  self.assertEqual(self.db.execute('SELECT role FROM users WHERE id=2').fetchone()[0],'admin')
 def test_no_self_demote(self):
  with self.assertRaises(ValueError):set_account_role(self.db,1,1,'reception')
 def test_nonadmin_denied(self):
  with self.assertRaises(PermissionError):list_accounts(self.db,2)
  with self.assertRaises(PermissionError):reset_account_password(self.db,2,1,'Strong&Pass1234','Strong&Pass1234')
 def test_password_reset_and_audit(self):
  reset_account_password(self.db,1,2,'Strong&Pass1234','Strong&Pass1234')
  self.assertNotEqual(self.db.execute('SELECT password_hash FROM users WHERE id=2').fetchone()[0],'hash')
  self.assertEqual(self.db.execute("SELECT event FROM security_events ORDER BY id DESC LIMIT 1").fetchone()[0],'password_reset')
 def test_invalid_role(self):
  with self.assertRaises(ValueError):set_account_role(self.db,1,2,'superuser')
 def test_no_password_in_audit(self):
  reset_account_password(self.db,1,2,'Strong&Pass1234','Strong&Pass1234')
  self.assertNotIn('Strong&Pass1234',str(self.db.execute('SELECT * FROM security_events').fetchall()))
