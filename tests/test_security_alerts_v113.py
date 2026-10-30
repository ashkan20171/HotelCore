import sqlite3
import unittest
from security_alerts_v113 import migrate,get_threshold,set_threshold,alert_history

class AlertSettingsTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,role TEXT,active INTEGER)')
        self.db.executemany('INSERT INTO users VALUES(?,?,?)',[(1,'admin',1),(2,'reception',1),(3,'admin',0)])
        migrate(self.db)
        self.addCleanup(self.db.close)
    def test_default(self):self.assertEqual(get_threshold(self.db,1),5)
    def test_update(self):
        set_threshold(self.db,1,12)
        self.assertEqual(get_threshold(self.db,1),12)
    def test_invalid(self):
        for value in (0,101,True,'5'):
            with self.assertRaises(ValueError):set_threshold(self.db,1,value)
    def test_reception_denied(self):
        with self.assertRaises(PermissionError):get_threshold(self.db,2)
        with self.assertRaises(PermissionError):alert_history(self.db,2)
    def test_disabled_admin_denied(self):
        with self.assertRaises(PermissionError):set_threshold(self.db,3,8)
    def test_invalid_severity(self):
        with self.assertRaises(ValueError):alert_history(self.db,1,severity='normal')
