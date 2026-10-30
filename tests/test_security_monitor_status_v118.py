import sqlite3
import unittest
from security_monitor_status_v118 import retry_delay_seconds, classify_error, record_failure, list_failures

class MonitorStatusTests(unittest.TestCase):
    def test_backoff(self):
        self.assertEqual([retry_delay_seconds(i) for i in range(1,5)], [5,10,20,40])
        self.assertEqual(retry_delay_seconds(50),300)
    def test_invalid(self):
        for value in (0,-1,True):
            with self.assertRaises(ValueError):retry_delay_seconds(value)
    def test_classification(self):
        self.assertEqual(classify_error('PermissionError: denied'),'authorization')
        self.assertEqual(classify_error('database is locked'),'transient')
        self.assertEqual(classify_error('unknown'),'other')
    def test_reject_non_admin(self):
        with sqlite3.connect(':memory:') as db:
            with self.assertRaises((PermissionError,sqlite3.Error)):
                record_failure(db,123,'error')
    def test_reject_invalid_limit(self):
        with sqlite3.connect(':memory:') as db:
            with self.assertRaises((PermissionError,sqlite3.Error,ValueError)):
                list_failures(db,123,0)
