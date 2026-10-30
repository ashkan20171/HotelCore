"""Consistently close short-lived SQLite connections, including on failure."""
import sqlite3
from contextlib import contextmanager

@contextmanager
def open_dashboard_db(path, *, read_only=False, timeout=5):
    conn=sqlite3.connect(str(path),timeout=timeout)
    try:
        if read_only:
            conn.execute('PRAGMA query_only=ON')
        yield conn
    finally:
        conn.close()
