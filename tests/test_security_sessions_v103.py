import sqlite3
import unittest
from datetime import datetime,timezone,timedelta
from security_sessions import migrate,create_session,validate_session,revoke_session,revoke_user_sessions,record_login,recent_login_events,list_sessions
from user_access_management import migrate as migrate_access,set_account_active,reset_account_password

class SessionTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.addCleanup(self.db.close)
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,password_hash TEXT,salt TEXT,role TEXT)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?,?)',[
   (1,'admin','hash','salt','admin'),(2,'staff','hash','salt','reception')])
  migrate_access(self.db);migrate(self.db)
  self.now=datetime(2026,10,23,tzinfo=timezone.utc)
 def test_valid_session(self):
  token=create_session(self.db,2,now=self.now)
  self.assertTrue(validate_session(self.db,token,now=self.now))
  self.assertFalse(validate_session(self.db,'not-a-session',now=self.now))
 def test_expiry(self):
  token=create_session(self.db,2,now=self.now,lifetime_hours=1)
  self.assertFalse(validate_session(self.db,token,now=self.now+timedelta(hours=2)))
 def test_revoke(self):
  token=create_session(self.db,2,now=self.now)
  revoke_session(self.db,token,now=self.now)
  self.assertFalse(validate_session(self.db,token,now=self.now))
 def test_disable_revokes(self):
  token=create_session(self.db,2,now=self.now)
  set_account_active(self.db,1,2,False)
  self.assertFalse(validate_session(self.db,token,now=self.now))
 def test_reset_revokes(self):
  token=create_session(self.db,2,now=self.now)
  reset_account_password(self.db,1,2,'Strong&Pass1234','Strong&Pass1234')
  self.assertFalse(validate_session(self.db,token,now=self.now))
 def test_admin_only_audit(self):
  record_login(self.db,2,'success',now=self.now)
  self.assertEqual(len(recent_login_events(self.db,1)),1)
  with self.assertRaises(PermissionError):recent_login_events(self.db,2)
  with self.assertRaises(PermissionError):list_sessions(self.db,2,1)
 def test_invalid_outcome(self):
  with self.assertRaises(ValueError):record_login(self.db,2,'unknown')
 def test_invalid_lifetime(self):
  with self.assertRaises(ValueError):create_session(self.db,2,lifetime_hours=0)
