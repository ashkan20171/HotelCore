import sqlite3, tempfile, unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from security_report_v110 import daily_login_trends, write_security_pdf

class SecurityReportTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.addCleanup(self.db.close)
  self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT,active INTEGER)')
  self.db.executemany('INSERT INTO users VALUES(?,?,?,?)',[(1,'admin','admin',1),(2,'staff','reception',1)])
  self.db.execute('CREATE TABLE login_events(id INTEGER PRIMARY KEY,user_id INTEGER,outcome TEXT,occurred_at TEXT)')
  self.now=datetime(2026,10,23,12,tzinfo=timezone.utc)
  self.db.executemany('INSERT INTO login_events(user_id,outcome,occurred_at) VALUES(?,?,?)',[(2,'failure',self.now.isoformat()),(2,'success',(self.now-timedelta(days=1)).isoformat())])
 def test_trends(self):
  result=daily_login_trends(self.db,1,days=2,now=self.now)
  self.assertEqual(result,[('2026-10-22',1,0,0),('2026-10-23',0,1,0)])
 def test_reception_cannot_read(self):
  with self.assertRaises(PermissionError):daily_login_trends(self.db,2,now=self.now)
 def test_validation(self):
  with self.assertRaises(ValueError):daily_login_trends(self.db,1,days=91)
 def test_pdf(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'report.pdf'
   self.assertEqual(write_security_pdf(path,self.db,1,days=2,now=self.now,language='en'),2)
   self.assertTrue(path.read_bytes().startswith(b'%PDF'))
