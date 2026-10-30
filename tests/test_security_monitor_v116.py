import sqlite3
import unittest
from datetime import datetime, timezone
from security_monitor_v116 import get_settings, set_settings, poll
from security_alerts_v113 import migrate as alert_migrate


class SecurityMonitorTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,role TEXT,active INTEGER)')
        self.db.executemany('INSERT INTO users VALUES(?,?,?,?)',
                            [(1,'admin','admin',1),(2,'staff','reception',1),(3,'off','admin',0)])
        self.db.execute('CREATE TABLE login_events(id INTEGER PRIMARY KEY,user_id INTEGER,outcome TEXT,occurred_at TEXT)')
        alert_migrate(self.db)

    def test_defaults_and_save(self):
        self.assertEqual(get_settings(self.db,1),{'enabled':True,'interval_seconds':300})
        self.assertEqual(set_settings(self.db,1,enabled=False,interval_seconds=60)['interval_seconds'],60)
        self.assertFalse(get_settings(self.db,1)['enabled'])

    def test_invalid_settings(self):
        for value in (0,59,3601,True,'300'):
            with self.assertRaises(ValueError):set_settings(self.db,1,enabled=True,interval_seconds=value)
        with self.assertRaises(ValueError):set_settings(self.db,1,enabled=1,interval_seconds=300)

    def test_permissions(self):
        for actor in (2,3):
            with self.assertRaises(PermissionError):get_settings(self.db,actor)
            with self.assertRaises(PermissionError):set_settings(self.db,actor,enabled=True,interval_seconds=300)
            with self.assertRaises(PermissionError):poll(self.db,actor)

    def test_disabled_poll_does_not_evaluate(self):
        set_settings(self.db,1,enabled=False,interval_seconds=60)
        self.assertEqual(poll(self.db,1),{'enabled':False,'unread':None,'alert':None})

    def test_poll_idempotent_and_no_duplicate_inbox(self):
        now=datetime(2026,10,23,12,tzinfo=timezone.utc)
        for _ in range(7):
            self.db.execute('INSERT INTO login_events(user_id,outcome,occurred_at) VALUES(?,?,?)',
                            (2,'failure',now.isoformat()))
        a=poll(self.db,1,now=now)
        b=poll(self.db,1,now=now)
        self.assertTrue(a['enabled'])
        self.assertEqual(a['unread'],b['unread'])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM security_notifications').fetchone()[0],a['unread'])
