"""Background, independently authorized health analytics (no Qt widget access)."""
import sqlite3
import threading
from datetime import datetime, timezone
from operation_guard import authorize_action
from system_health_analytics_v121 import compare_periods
from system_health_trends_v122 import daily_trends

def load_dashboard(db_path, actor_id, token, days, threshold, cancel_event=None):
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('days must be 1..90')
    if type(threshold) is not int or not 0 <= threshold <= 100:
        raise ValueError('threshold must be 0..100')
    conn = sqlite3.connect(str(db_path), timeout=5)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        if cancel_event is not None:
            conn.set_progress_handler(lambda: 1 if cancel_event.is_set() else 0, 200)
        authorize_action(conn, actor_id, token, 'security.view')
        # A single UTC anchor keeps chart and comparison periods consistent.
        now = datetime.now(timezone.utc)
        result = compare_periods(conn, actor_id, days=days, warning_threshold=threshold, now=now)
        series = daily_trends(conn, actor_id, days=days, now=now)
        if cancel_event is not None and cancel_event.is_set():
            raise sqlite3.OperationalError('interrupted')
        return {'result':result, 'series':series, 'days':days, 'threshold':threshold}
    finally:
        conn.close()

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    QThread = None
    Signal = None

if QThread is not None:
    class HealthDashboardWorker(QThread):
        succeeded = Signal(object)
        failed = Signal(str)
        def __init__(self, db_path, actor_id, token, days, threshold, parent=None):
            super().__init__(parent)
            self.cancel_event = threading.Event()
            self.args = (db_path, actor_id, token, days, threshold, self.cancel_event)
        def cancel(self):
            self.cancel_event.set()
        def run(self):
            try:
                self.succeeded.emit(load_dashboard(*self.args))
            except (PermissionError, ValueError, sqlite3.Error) as exc:
                # Never expose tokens or SQL exception details in the UI.
                self.failed.emit('Access denied or health data unavailable' if isinstance(exc, PermissionError) else 'Health data unavailable')
