import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from security_monitor_worker_v117 import run_monitor_check


class WorkerTests(unittest.TestCase):
    def test_separate_connection_and_result(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test.db'
            with sqlite3.connect(path) as conn:
                conn.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, role TEXT, active INTEGER)')
                conn.execute("INSERT INTO users VALUES(1,'admin','admin',1)")
                conn.execute('CREATE TABLE login_events(id INTEGER PRIMARY KEY,user_id INTEGER,outcome TEXT,occurred_at TEXT)')
            with patch('operation_guard.authorize_action') as guard:
                result=run_monitor_check(path,1,'token')
            self.assertTrue(result['enabled'])
            self.assertEqual(result['unread'],0)
            guard.assert_called_once()

    def test_permission_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test.db'
            with sqlite3.connect(path) as conn:
                conn.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, role TEXT, active INTEGER)')
                conn.execute("INSERT INTO users VALUES(1,'admin','admin',1)")
            with patch('operation_guard.authorize_action',side_effect=PermissionError('expired')):
                with self.assertRaises(PermissionError):run_monitor_check(path,1,'expired')
