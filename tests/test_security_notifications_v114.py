import sqlite3
import unittest
from security_notifications_v114 import migrate,sync_alerts,unread_count,inbox,mark_read,acknowledge
from security_alerts_v113 import migrate as alerts_migrate

class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,role TEXT,active INTEGER)')
        self.db.executemany('INSERT INTO users VALUES(?,?,?)',[(1,'admin',1),(2,'reception',1),(3,'admin',0)])
        alerts_migrate(self.db)
        self.db.execute("INSERT INTO security_alert_history(actor_id,days,severity,failed_attempts,previous_attempts,threshold) VALUES(1,7,'high',9,1,5)")
        self.db.execute("INSERT INTO security_alert_history(actor_id,days,severity,failed_attempts,previous_attempts,threshold) VALUES(1,7,'review',5,2,5)")
    def test_sync_is_idempotent(self):
        self.assertEqual(sync_alerts(self.db,1),2)
        self.assertEqual(sync_alerts(self.db,1),2)
        self.assertEqual(len(inbox(self.db,1)),2)
    def test_read_and_ack(self):
        sync_alerts(self.db,1)
        n=inbox(self.db,1)[0][0]
        mark_read(self.db,1,n)
        self.assertEqual(unread_count(self.db,1),1)
        acknowledge(self.db,1,n)
        self.assertEqual(len(inbox(self.db,1,status='acknowledged')),1)
        acknowledge(self.db,1,n)
        self.assertEqual(len(inbox(self.db,1,status='acknowledged')),1)
    def test_filters(self):
        sync_alerts(self.db,1)
        self.assertEqual(len(inbox(self.db,1,severity='high')),1)
        self.assertEqual(len(inbox(self.db,1,status='unread')),2)
    def test_permissions(self):
        for user in (2,3):
            with self.assertRaises(PermissionError):sync_alerts(self.db,user)
            with self.assertRaises(PermissionError):inbox(self.db,user)
    def test_invalid_values(self):
        sync_alerts(self.db,1)
        for kw in ({'status':'unknown'},{'severity':'low'},{'limit':0}):
            with self.assertRaises(ValueError):inbox(self.db,1,**kw)
        for item in (0,True,999):
            with self.assertRaises(ValueError):mark_read(self.db,1,item)
