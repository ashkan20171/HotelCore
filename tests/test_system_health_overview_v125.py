import unittest
import sqlite3
import threading
from system_health_overview_v125 import load_overview
from system_health_async_v124 import load_dashboard

class Stage125Tests(unittest.TestCase):
    def test_overview_cancellation_set(self):
        flag = threading.Event(); flag.set()
        with self.assertRaises(sqlite3.OperationalError):
            load_overview(':memory:', 1, 'token', cancel_event=flag)
    def test_dashboard_rejects_invalid_days(self):
        with self.assertRaises(ValueError):
            load_dashboard(':memory:', 1, 'token', 0, 20)
    def test_dashboard_rejects_invalid_threshold(self):
        with self.assertRaises(ValueError):
            load_dashboard(':memory:', 1, 'token', 7, 101)
