import sqlite3
import unittest
from datetime import datetime, timezone
from security_chart_v111 import chart_data


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.addCleanup(self.conn.close)
        self.conn.executescript('''CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, role TEXT, active INTEGER);
        CREATE TABLE login_events(id INTEGER PRIMARY KEY,user_id INTEGER,outcome TEXT,occurred_at TEXT);''')
        self.conn.executemany('INSERT INTO users VALUES(?,?,?,?)', [(1,'admin','admin',1),(2,'staff','reception',1)])
        self.now=datetime(2026,10,23,12,0,tzinfo=timezone.utc)

    def test_empty(self):
        result=chart_data(self.conn,1,days=7,now=self.now)
        self.assertEqual(len(result['series']),7)
        self.assertEqual(result['success_rate'],0)

    def test_totals_and_rate(self):
        self.conn.executemany('INSERT INTO login_events(user_id,outcome,occurred_at) VALUES(?,?,?)',
                              [(2,'success','2026-10-23T08:00:00+00:00'),(2,'failure','2026-10-23T08:01:00+00:00')])
        result=chart_data(self.conn,1,days=1,now=self.now)
        self.assertEqual(result['totals']['success'],1)
        self.assertEqual(result['success_rate'],50.0)
        self.assertEqual(result['peak_failures'],1)

    def test_non_admin(self):
        with self.assertRaises(PermissionError):chart_data(self.conn,2,now=self.now)

    def test_invalid_days(self):
        with self.assertRaises(ValueError):chart_data(self.conn,1,days=91,now=self.now)
