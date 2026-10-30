import sqlite3
import unittest
from unittest.mock import patch
from security_admin_presentation import account_counts, account_rows
from security_action_service import execute_admin_action
from user_access_management import migrate as migrate_access
from security_sessions import migrate as migrate_sessions

class SecurityAdminTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT,salt TEXT,role TEXT)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?,?)',[(1,'boss','h','s','admin'),(2,'staff','h','s','reception'),(3,'admin2','h','s','admin')])
  migrate_access(self.db);migrate_sessions(self.db)
 def run_action(self,action,target,value=None,confirmation=None,actor=1):
  with patch('security_action_service.authorize_action') as guard:
   result=execute_admin_action(self.db,actor,'token',action,target,value=value,confirmation=confirmation)
   guard.assert_called_once_with(self.db,actor,'token','users.create')
   return result
 def test_counts(self):
  rows=[(1,'a','admin',1),(2,'b','reception',0),(3,'c','admin',1)]
  self.assertEqual(account_counts(rows),{'active':2,'disabled':1,'admins':2})
 def test_rows_bilingual(self):
  rows=[(1,'a','admin',1),(2,'b','reception',0)]
  self.assertEqual(account_rows(rows,fa=False)[1][-1],'Disabled')
  self.assertEqual(account_rows(rows,fa=True)[0][-1],'فعال')
 def test_toggle(self):
  self.run_action('account.toggle',2,False)
  self.assertEqual(self.db.execute('SELECT active FROM users WHERE id=2').fetchone()[0],0)
 def test_role(self):
  self.run_action('account.role',2,'admin')
  self.assertEqual(self.db.execute('SELECT role FROM users WHERE id=2').fetchone()[0],'admin')
 def test_password(self):
  self.run_action('account.password',2,'Strong&Pass1234','Strong&Pass1234')
  self.assertNotEqual(self.db.execute('SELECT password_hash FROM users WHERE id=2').fetchone()[0],'h')
 def test_revoke(self):
  self.run_action('session.revoke',2)
  self.assertEqual(self.db.execute('SELECT event FROM security_events ORDER BY id DESC LIMIT 1').fetchone()[0],'sessions_revoked')
 def test_unknown_action(self):
  with self.assertRaises(ValueError):execute_admin_action(self.db,1,'token','unknown',2)
 def test_guard_denial(self):
  with patch('security_action_service.authorize_action',side_effect=PermissionError):
   with self.assertRaises(PermissionError):execute_admin_action(self.db,1,'bad','account.toggle',2,value=False)
  self.assertEqual(self.db.execute('SELECT active FROM users WHERE id=2').fetchone()[0],1)
 def test_invalid_toggle(self):
  with self.assertRaises(ValueError):self.run_action('account.toggle',2,'no')
 def test_nonexistent_revoke(self):
  with self.assertRaises(ValueError):self.run_action('session.revoke',999)
