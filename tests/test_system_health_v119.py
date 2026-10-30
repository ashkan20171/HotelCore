import sqlite3
import unittest
from datetime import datetime,timezone
from system_health_v119 import snapshot,history

class SystemHealthTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,role TEXT,active INTEGER)')
        self.db.executemany('INSERT INTO users VALUES(?,?,?)',[(1,'admin',1),(2,'reception',1)])
    def tearDown(self):self.db.close()
    def test_snapshot_and_history(self):
        result=snapshot(self.db,1,monitor_state='healthy')
        self.assertEqual(result['database_status'],'ok')
        self.assertEqual(result['monitor_state'],'healthy')
        self.assertEqual(result['failure_count'],0)
        self.assertEqual(len(history(self.db,1)),1)
    def test_not_saved_when_requested(self):
        snapshot(self.db,1,save=False)
        self.assertEqual(history(self.db,1),[])
    def test_non_admin_denied(self):
        with self.assertRaises(PermissionError):snapshot(self.db,2)
        with self.assertRaises(PermissionError):history(self.db,2)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):snapshot(self.db,1,monitor_state='')
        with self.assertRaises(ValueError):snapshot(self.db,1,now=datetime.now())
        with self.assertRaises(ValueError):history(self.db,1,limit=True)
    def test_history_order_and_cap(self):
        for _ in range(3):snapshot(self.db,1,monitor_state='running')
        self.assertEqual(len(history(self.db,1,limit=2)),2)
    def test_failure_count(self):
        from security_monitor_status_v118 import migrate
        migrate(self.db)
        self.db.execute("INSERT INTO security_monitor_failures(recorded_at,category,detail,retry_attempt) VALUES('x','other','other',0)")
        self.assertEqual(snapshot(self.db,1)['failure_count'],1)
