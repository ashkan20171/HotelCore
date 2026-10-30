import sqlite3
import unittest
from datetime import datetime, timezone
from login_security import migrate_security_events, record_security_event, recent_security_events

class LoginSecurityEventsV165Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        migrate_security_events(self.db)

    def tearDown(self):
        self.db.close()

    def test_records_failure_without_credentials(self):
        record_security_event(self.db, '  unknown.user  ', 'failure',
                              datetime(2026, 10, 29, tzinfo=timezone.utc),
                              'invalid_credentials_or_inactive')
        event = recent_security_events(self.db)[0]
        self.assertEqual(event['attempted_username'], 'unknown.user')
        self.assertEqual(event['outcome'], 'failure')
        self.assertNotIn('password', str(event).lower())

    def test_truncates_long_username_and_detail(self):
        record_security_event(self.db, 'x' * 200, 'locked', detail='d' * 100)
        event = recent_security_events(self.db)[0]
        self.assertEqual(len(event['attempted_username']), 128)
        self.assertEqual(len(event['detail']), 40)

    def test_empty_username_has_safe_marker(self):
        record_security_event(self.db, ' ', 'failure')
        self.assertEqual(recent_security_events(self.db)[0]['attempted_username'], '<empty>')

    def test_filter_and_order(self):
        record_security_event(self.db, 'user', 'failure')
        record_security_event(self.db, 'user', 'success')
        self.assertEqual(len(recent_security_events(self.db, outcome='failure')), 1)
        self.assertEqual(recent_security_events(self.db)[0]['outcome'], 'success')

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError): record_security_event(self.db, 'user', 'bad')
        with self.assertRaises(ValueError): recent_security_events(self.db, limit=0)
        with self.assertRaises(ValueError): recent_security_events(self.db, outcome='bad')

    def test_migration_is_idempotent(self):
        migrate_security_events(self.db)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='login_security_events'").fetchone()[0], 1)

if __name__ == '__main__':
    unittest.main()
