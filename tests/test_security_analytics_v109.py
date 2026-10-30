import unittest,sqlite3
from datetime import datetime,timezone,timedelta
from security_analytics_v109 import security_activity
class AnalyticsTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:');self.addCleanup(self.c.close)
  self.c.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT,active INTEGER)')
  self.c.executemany('INSERT INTO users VALUES(?,?,?,?)',[(1,'admin','admin',1),(2,'staff','reception',1)])
  self.c.execute('CREATE TABLE login_events(id INTEGER PRIMARY KEY,user_id INTEGER,outcome TEXT,occurred_at TEXT)')
  now=datetime(2026,10,23,tzinfo=timezone.utc);self.now=now
  self.c.executemany('INSERT INTO login_events(user_id,outcome,occurred_at) VALUES(?,?,?)',[(2,'failure',(now-timedelta(hours=1)).isoformat())]*5+[(2,'success',(now-timedelta(days=15)).isoformat())])
 def test_counts(self):
  result=security_activity(self.c,1,now=self.now)
  self.assertEqual(result['totals']['failure'],5)
  self.assertEqual(result['totals']['success'],0)
  self.assertEqual(result['review_candidates'],[('staff',5)])
 def test_admin_only(self):
  with self.assertRaises(PermissionError):security_activity(self.c,2,now=self.now)
 def test_limits(self):
  with self.assertRaises(ValueError):security_activity(self.c,1,days=0)
  with self.assertRaises(ValueError):security_activity(self.c,1,limit=1000)
 def test_user_filter(self):
  self.assertEqual(security_activity(self.c,1,username='nobody',now=self.now)['records'],[])
