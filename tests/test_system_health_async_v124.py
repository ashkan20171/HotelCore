import unittest
from unittest.mock import patch
from system_health_async_v124 import load_dashboard

class HealthAsyncTests(unittest.TestCase):
    def test_rejects_invalid_days_before_connect(self):
        with self.assertRaises(ValueError):
            load_dashboard('unused.db', 1, 'token', 0, 20)
        with self.assertRaises(ValueError):
            load_dashboard('unused.db', 1, 'token', 91, 20)

    def test_rejects_invalid_threshold_before_connect(self):
        with self.assertRaises(ValueError):
            load_dashboard('unused.db', 1, 'token', 7, 101)
        with self.assertRaises(ValueError):
            load_dashboard('unused.db', 1, 'token', 7, True)

    def test_fail_closed_without_authorization(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises((PermissionError, ValueError, __import__('sqlite3').Error)):
                load_dashboard(Path(folder)/'health.db', 1, 'invalid', 7, 20)
