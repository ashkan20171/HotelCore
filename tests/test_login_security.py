import unittest,sqlite3
from datetime import datetime,timezone,timedelta
from login_security import migrate,is_locked,record_failure,clear_failures

class LoginSecurityTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:');migrate(self.c)
  self.now=datetime(2026,10,20,tzinfo=timezone.utc)
 def tearDown(self):self.c.close()
 def test_new_user_not_locked(self):self.assertFalse(is_locked(self.c,'admin',self.now))
 def test_four_failures_not_locked(self):
  for _ in range(4):self.assertFalse(record_failure(self.c,'admin',self.now))
  self.assertFalse(is_locked(self.c,'admin',self.now))
 def test_five_failures_lock(self):
  for _ in range(5):record_failure(self.c,'admin',self.now)
  self.assertTrue(is_locked(self.c,'admin',self.now))
 def test_expiry(self):
  for _ in range(5):record_failure(self.c,'admin',self.now)
  self.assertFalse(is_locked(self.c,'admin',self.now+timedelta(minutes=16)))
 def test_success_resets(self):
  record_failure(self.c,'admin',self.now);clear_failures(self.c,'admin')
  self.assertEqual(self.c.execute('SELECT count(*) FROM login_attempts').fetchone()[0],0)
 def test_users_independent(self):
  for _ in range(5):record_failure(self.c,'admin',self.now)
  self.assertFalse(is_locked(self.c,'other',self.now))
 def test_locked_attempt_does_not_extend_window(self):
  for _ in range(5):record_failure(self.c,'admin',self.now)
  original=self.c.execute('SELECT locked_until FROM login_attempts').fetchone()[0]
  record_failure(self.c,'admin',self.now+timedelta(minutes=1))
  self.assertEqual(self.c.execute('SELECT locked_until FROM login_attempts').fetchone()[0],original)
