import sqlite3
import unittest
from login_security import migrate_security_events, record_security_event
from security_admin_panel_v166 import security_event_detail

class SecurityEventDetailV168Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        migrate_security_events(self.db)
        record_security_event(self.db, 'ashkan', 'failure', detail='invalid_credentials')

    def tearDown(self):
        self.db.close()

    def test_returns_matching_event(self):
        row = security_event_detail(self.db, 1)
        self.assertEqual(row['attempted_username'], 'ashkan')
        self.assertEqual(row['outcome'], 'failure')
        self.assertEqual(row['detail'], 'invalid_credentials')

    def test_missing_event_returns_none(self):
        self.assertIsNone(security_event_detail(self.db, 999))

    def test_rejects_invalid_ids(self):
        for value in (0, -1, True, '1', 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                security_event_detail(self.db, value)

    def test_parameterized_lookup(self):
        # Non-integer values are rejected before any SQL is executed.
        with self.assertRaises(ValueError):
            security_event_detail(self.db, '1 OR 1=1')

if __name__ == '__main__':
    unittest.main()
