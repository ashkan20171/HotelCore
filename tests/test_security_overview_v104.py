import sqlite3
import unittest
from datetime import datetime, timezone, timedelta
from security_sessions import migrate as sessions_migrate, create_session, record_login
from user_access_management import migrate as access_migrate
from security_overview import require_permission, security_summary, recent_security_changes

class SecurityOverviewTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT, password_hash TEXT,salt TEXT,role TEXT)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?,?)',[(1,'admin','h','s','admin'),(2,'staff','h','s','reception')])
  access_migrate(self.db);sessions_migrate(self.db)
  self.now=datetime(2026,10,23,12,tzinfo=timezone.utc)
 def test_admin_permission(self):
  self.assertTrue(require_permission(self.db,1,'security.view'))
 def test_reception_denied(self):
  with self.assertRaises(PermissionError):require_permission(self.db,2,'security.view')
 def test_unknown_permission(self):
  with self.assertRaises(ValueError):require_permission(self.db,1,'nonsense')
 def test_disabled_admin_denied(self):
  self.db.execute('UPDATE users SET active=0 WHERE id=1')
  with self.assertRaises(PermissionError):require_permission(self.db,1,'users.manage')
 def test_summary_window(self):
  record_login(self.db,1,'success',now=self.now-timedelta(days=2))
  record_login(self.db,2,'failure',now=self.now-timedelta(days=1))
  record_login(self.db,2,'locked',now=self.now-timedelta(days=10))
  create_session(self.db,2,now=self.now-timedelta(hours=1))
  data=security_summary(self.db,1,now=self.now)
  self.assertEqual((data['success'],data['failure'],data['locked'],data['active_sessions']),(1,1,0,1))
  self.assertEqual(data['total_accounts'],2)
 def test_disabled_sessions_not_counted(self):
  create_session(self.db,2,now=self.now)
  self.db.execute('UPDATE users SET active=0 WHERE id=2')
  self.assertEqual(security_summary(self.db,1,now=self.now)['active_sessions'],0)
 def test_no_reception_summary(self):
  with self.assertRaises(PermissionError):security_summary(self.db,2,now=self.now)
 def test_invalid_window(self):
  for n in (0,91,True):
   with self.subTest(n=n),self.assertRaises(ValueError):security_summary(self.db,1,days=n,now=self.now)
 def test_recent_changes(self):
  self.db.execute("INSERT INTO security_events(actor_id,target_id,event) VALUES(1,2,'account_disabled')")
  rows=recent_security_changes(self.db,1)
  self.assertEqual(rows[0][1:],('admin','staff','account_disabled'))
 def test_recent_changes_restricted(self):
  with self.assertRaises(PermissionError):recent_security_changes(self.db,2)
 def test_recent_changes_limit(self):
  with self.assertRaises(ValueError):recent_security_changes(self.db,1,limit=101)
