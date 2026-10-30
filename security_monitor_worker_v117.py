"""Isolated security poll worker; SQLite connection belongs to the worker thread."""
import sqlite3


def run_monitor_check(database_path, actor_id, session_token):
    """Return the polling result, using an independent, short-lived connection."""
    from operation_guard import authorize_action
    from security_monitor_v116 import poll
    with sqlite3.connect(str(database_path), timeout=5.0) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=5000')
        authorize_action(conn, actor_id, session_token, 'security.view')
        return poll(conn, actor_id)


try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    QThread = None
    Signal = None

if QThread is not None:
    class SecurityMonitorWorker(QThread):
        """One poll per instance. Only emits data; never touches widgets."""
        succeeded = Signal(object)
        failed = Signal(str)

        def __init__(self, database_path, actor_id, session_token, parent=None):
            super().__init__(parent)
            self.database_path = str(database_path)
            self.actor_id = actor_id
            self.session_token = session_token

        def run(self):
            try:
                result = run_monitor_check(self.database_path, self.actor_id, self.session_token)
            except (PermissionError, ValueError, sqlite3.Error, OSError) as exc:
                self.failed.emit(type(exc).__name__ + ': ' + str(exc))
            except Exception as exc:
                self.failed.emit(type(exc).__name__ + ': unexpected monitoring failure')
            else:
                self.succeeded.emit(result)
else:
    SecurityMonitorWorker = None
