"""Authorized, cancellable, atomic system-health exports (stage 126)."""
import os
import sqlite3
import tempfile
import threading
from pathlib import Path

from operation_guard import authorize_action
from system_health_reports_v120 import write_excel, write_pdf


class ExportCancelled(Exception):
    """Export cancelled before publishing the completed report."""


def export_report(db_path, actor_id, token, destination, fmt, *, language='fa',
                  cancel_event=None, progress=None, writer=None):
    """Write to a sibling temporary file and publish only on complete success.

    Cancellation is cooperative: SQLite queries can be interrupted, but the
    PDF/XLSX renderer may finish its current operation before cancellation wins.
    Existing destination files are never truncated on failure/cancellation.
    """
    if fmt not in ('xlsx', 'pdf'):
        raise ValueError('Unsupported report format')
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    target = Path(destination)
    if not target.name or not target.parent.is_dir():
        raise ValueError('Invalid export destination')
    cancelled = cancel_event or threading.Event()
    def check():
        if cancelled.is_set():
            raise ExportCancelled('Export cancelled')
    def notify(value):
        if progress is not None:
            progress(value)
    check()
    notify(5)
    fd, temporary = tempfile.mkstemp(prefix='.hotel_health_', suffix='.' + fmt,
                                    dir=str(target.parent))
    os.close(fd)
    try:
        with sqlite3.connect(str(db_path), timeout=5) as conn:
            conn.set_progress_handler(lambda: int(cancelled.is_set()), 200)
            check()
            authorize_action(conn, actor_id, token, 'security.view')
            notify(25)
            check()
            render = writer or (write_excel if fmt == 'xlsx' else write_pdf)
            count = render(temporary, conn, actor_id, language=language)
            notify(85)
            check()
        check()
        os.replace(temporary, target)
        notify(100)
        return count
    except sqlite3.OperationalError as exc:
        if cancelled.is_set():
            raise ExportCancelled('Export cancelled') from exc
        raise
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    QThread = None
    Signal = None

if QThread is not None:
    class HealthExportWorker(QThread):
        progress = Signal(int)
        succeeded = Signal(int)
        failed = Signal(str)
        cancelled = Signal()

        def __init__(self, db_path, actor_id, token, destination, fmt, language, parent=None):
            super().__init__(parent)
            self.cancel_event = threading.Event()
            self.args = (db_path, actor_id, token, destination, fmt)
            self.language = language

        def cancel(self):
            self.cancel_event.set()

        def run(self):
            try:
                count = export_report(*self.args, language=self.language,
                                      cancel_event=self.cancel_event,
                                      progress=self.progress.emit)
                self.succeeded.emit(count)
            except ExportCancelled:
                self.cancelled.emit()
            except (PermissionError, ValueError, sqlite3.Error, OSError, ImportError) as exc:
                self.failed.emit(str(exc))
            except Exception:
                self.failed.emit('Unexpected report export failure')
