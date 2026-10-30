import sqlite3
import unittest
from operation_guard import authorize_action,ACTION_PERMISSIONS
from security_sessions import migrate as migrate_sessions,create_session,revoke_session
from user_access_management import migrate as migrate_access,set_account_active,set_account_role

class OperationGuardTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,password_hash TEXT,salt TEXT,role TEXT)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?,?)',[(1,'admin','h','s','admin'),(2,'staff','h','s','reception')])
  migrate_access(self.db);migrate_sessions(self.db)
  self.admin=create_session(self.db,1)
  self.staff=create_session(self.db,2)
 def test_admin_finance(self):
  self.assertTrue(authorize_action(self.db,1,self.admin,'finance.expense'))
 def test_reception_reservations(self):
  self.assertTrue(authorize_action(self.db,2,self.staff,'reservations.payment'))
 def test_reception_finance_denied(self):
  with self.assertRaises(PermissionError):authorize_action(self.db,2,self.staff,'finance.export')
 def test_reception_users_denied(self):
  with self.assertRaises(PermissionError):authorize_action(self.db,2,self.staff,'users.create')
 def test_revoked_denied(self):
  revoke_session(self.db,self.staff)
  with self.assertRaises(PermissionError):authorize_action(self.db,2,self.staff,'reservations.create')
 def test_disabled_denied(self):
  set_account_active(self.db,1,2,False)
  with self.assertRaises(PermissionError):authorize_action(self.db,2,self.staff,'reservations.payment')
 def test_role_change_revokes(self):
  set_account_role(self.db,1,2,'admin')
  with self.assertRaises(PermissionError):authorize_action(self.db,2,self.staff,'finance.export')
 def test_missing_token(self):
  with self.assertRaises(PermissionError):authorize_action(self.db,1,None,'users.create')
 def test_unknown_action(self):
  with self.assertRaises(ValueError):authorize_action(self.db,1,self.admin,'unknown')
 def test_permission_map(self):
  self.assertEqual(len(ACTION_PERMISSIONS),11)
