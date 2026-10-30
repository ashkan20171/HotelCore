import sqlite3,unittest,tempfile
from pathlib import Path
from executive_db_connection_v140 import open_dashboard_db

class DbLifecycleTests(unittest.TestCase):
    def test_close_on_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'a.db'
            with open_dashboard_db(path) as conn:
                conn.execute('CREATE TABLE t(id INTEGER)')
                connection=conn
            with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
    def test_close_on_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'a.db'
            with self.assertRaisesRegex(RuntimeError,'boom'):
                with open_dashboard_db(path) as conn:
                    connection=conn
                    raise RuntimeError('boom')
            with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
    def test_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'a.db'
            with open_dashboard_db(path) as conn:conn.execute('CREATE TABLE t(id INTEGER)')
            with open_dashboard_db(path,read_only=True) as conn:
                self.assertEqual(conn.execute('SELECT count(*) FROM t').fetchone()[0],0)
                with self.assertRaises(sqlite3.OperationalError):conn.execute('INSERT INTO t VALUES(1)')
