"""On-demand system health overview on a separate SQLite connection."""
import sqlite3
import threading
from operation_guard import authorize_action
from system_health_v119 import snapshot, history
from system_health_reports_v120 import report_data

def load_overview(db_path, actor_id, token, monitor_state='unknown', cancel_event=None):
    conn = sqlite3.connect(str(db_path), timeout=3)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        if cancel_event is not None:
            conn.set_progress_handler(lambda: 1 if cancel_event.is_set() else 0, 200)
            if cancel_event.is_set():
                raise sqlite3.OperationalError('interrupted')
        authorize_action(conn, actor_id, token, 'security.view')
        with conn:
            status = snapshot(conn, actor_id, monitor_state=monitor_state)
            rows = history(conn, actor_id, limit=20)
            metrics = report_data(conn, actor_id, limit=100)
        return {'status': status, 'rows': rows, 'metrics': metrics}
    finally:
        conn.close()

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    QThread = None
    Signal = None

if QThread is not None:
    class HealthOverviewWorker(QThread):
        succeeded = Signal(object)
        failed = Signal(str)
        def __init__(self, db_path, actor_id, token, monitor_state, parent=None):
            super().__init__(parent)
            self.cancel_event = threading.Event()
            self.args = (db_path, actor_id, token, monitor_state, self.cancel_event)
        def cancel(self):
            self.cancel_event.set()
        def run(self):
            try:
                self.succeeded.emit(load_overview(*self.args))
            except (PermissionError, ValueError, sqlite3.Error):
                self.failed.emit('Access denied or health data unavailable')
