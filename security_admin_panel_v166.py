"""Stage 166: security event reporting helpers and optional PySide6 admin dialog."""
from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from login_security import migrate_security_events

OUTCOMES = (None, 'failure', 'locked', 'success')


def security_event_report(conn, *, outcome=None, username=None, start=None, end=None, limit=500):
    """Return filtered authentication events and summary counts.

    start/end are inclusive ISO date or datetime strings. Date-only end values
    include the full day. Values are bound SQL parameters, never interpolated.
    """
    if outcome not in OUTCOMES:
        raise ValueError('Unsupported outcome')
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('limit must be between 1 and 1000')
    def normalize(value, is_end=False):
        if value is None or str(value).strip() == '': return None
        value = str(value).strip()
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError('Dates must be ISO-8601 date/time values') from exc
        if len(value) == 10 and is_end:
            value += 'T23:59:59.999999'
        elif len(value) == 10:
            value += 'T00:00:00'
        return value
    start_value, end_value = normalize(start), normalize(end, True)
    if start_value and end_value and start_value > end_value:
        raise ValueError('start must not be after end')
    migrate_security_events(conn)
    clauses, params = [], []
    if outcome is not None: clauses.append('outcome=?'); params.append(outcome)
    if username and str(username).strip():
        clauses.append('attempted_username LIKE ? ESCAPE \'\\\'')
        escaped = str(username).strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        params.append('%' + escaped[:128] + '%')
    if start_value: clauses.append('occurred_at>=?'); params.append(start_value)
    if end_value: clauses.append('occurred_at<=?'); params.append(end_value)
    where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
    rows = conn.execute('SELECT id,attempted_username,outcome,occurred_at,detail FROM login_security_events' + where + ' ORDER BY occurred_at DESC,id DESC LIMIT ?', (*params, limit)).fetchall()
    keys = ('id','attempted_username','outcome','occurred_at','detail')
    events = [dict(zip(keys, row)) for row in rows]
    # Summary follows active filters, not only the displayed page.
    counts = {key: 0 for key in ('failure','locked','success')}
    totals = conn.execute('SELECT outcome,COUNT(*) FROM login_security_events' + where + ' GROUP BY outcome', params).fetchall()
    counts.update({key: count for key, count in totals})
    return {'events': events, 'counts': counts, 'shown': len(events), 'limit': limit}


def security_event_detail(conn, event_id):
    """Return one security event by positive integer ID, or None if absent."""
    if type(event_id) is not int or event_id < 1:
        raise ValueError('event_id must be a positive integer')
    migrate_security_events(conn)
    row = conn.execute(
        'SELECT id,attempted_username,outcome,occurred_at,detail FROM login_security_events WHERE id=?',
        (event_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(zip(('id','attempted_username','outcome','occurred_at','detail'), row))


def _spreadsheet_safe(value):
    text = '' if value is None else str(value)
    if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + text
    return text


def export_security_events_csv(path, events, *, language='fa'):
    """Write selected events as UTF-8-BOM CSV, mitigating spreadsheet formulas."""
    if language not in ('fa', 'en'):
        raise ValueError('language must be fa or en')
    headers = (['شناسه','نام کاربری واردشده','نتیجه','زمان (UTC)','جزئیات'] if language == 'fa'
               else ['ID','Attempted username','Outcome','Timestamp (UTC)','Detail'])
    fields = ('id','attempted_username','outcome','occurred_at','detail')
    with open(Path(path), 'w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        for event in events:
            writer.writerow([_spreadsheet_safe(event.get(field)) for field in fields])

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QComboBox, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
        QMessageBox, QHeaderView, QCheckBox, QFormLayout, QTextEdit)
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

if PYSIDE_AVAILABLE:
    class SecurityAdminPanel(QDialog):
        """Standalone security report dialog; pass a live SQLite connection and language."""
        def __init__(self, conn, language='fa', parent=None):
            super().__init__(parent)
            self.conn, self.language, self._events = conn, language, []
            fa = language == 'fa'
            self.setWindowTitle('گزارش امنیتی' if fa else 'Security report')
            self.resize(1000, 620)
            root = QVBoxLayout(self)
            filters = QHBoxLayout()
            self.username = QLineEdit(); self.username.setPlaceholderText('نام کاربری' if fa else 'Username')
            self.outcome = QComboBox()
            self.outcome.addItems(['همه نتایج' if fa else 'All outcomes', 'ناموفق' if fa else 'Failure', 'قفل‌شده' if fa else 'Locked', 'موفق' if fa else 'Success'])
            self.start_enabled = QCheckBox('از تاریخ' if fa else 'From date')
            self.start = QDateEdit(); self.start.setCalendarPopup(True); self.start.setDisplayFormat('yyyy-MM-dd')
            self.end_enabled = QCheckBox('تا تاریخ' if fa else 'To date')
            self.end = QDateEdit(); self.end.setCalendarPopup(True); self.end.setDisplayFormat('yyyy-MM-dd')
            self.start.setEnabled(False); self.end.setEnabled(False)
            self.start_enabled.toggled.connect(self.start.setEnabled)
            self.end_enabled.toggled.connect(self.end.setEnabled)
            self.refresh_btn = QPushButton('جست‌وجو' if fa else 'Search')
            self.export_btn = QPushButton('خروجی CSV' if fa else 'Export CSV')
            for widget in (self.username, self.outcome, self.start_enabled, self.start, self.end_enabled, self.end, self.refresh_btn, self.export_btn): filters.addWidget(widget)
            root.addLayout(filters)
            self.summary = QLabel(); root.addWidget(self.summary)
            self.table = QTableWidget(0, 5)
            self.table.setHorizontalHeaderLabels(['شناسه','نام کاربری','نتیجه','زمان UTC','جزئیات'] if fa else ['ID','Username','Outcome','UTC timestamp','Detail'])
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            root.addWidget(self.table)
            self.refresh_btn.clicked.connect(self.refresh)
            self.export_btn.clicked.connect(self.export_csv)
            self.table.cellDoubleClicked.connect(self.show_event_detail)
            self.refresh()

        def refresh(self):
            outcome = (None, 'failure', 'locked', 'success')[self.outcome.currentIndex()]
            start = self.start.date().toString('yyyy-MM-dd') if self.start_enabled.isChecked() else None
            end = self.end.date().toString('yyyy-MM-dd') if self.end_enabled.isChecked() else None
            try: report = security_event_report(self.conn, outcome=outcome, username=self.username.text(), start=start, end=end)
            except (ValueError, Exception) as exc:
                QMessageBox.warning(self, self.windowTitle(), str(exc)); return
            self._events = report['events']; self.table.setRowCount(len(self._events))
            for row, event in enumerate(self._events):
                values = [event['id'], event['attempted_username'], event['outcome'], event['occurred_at'], event['detail']]
                for col, value in enumerate(values): self.table.setItem(row, col, QTableWidgetItem(str(value)))
            counts = report['counts']
            self.summary.setText(('نمایش: %d | ناموفق: %d | قفل‌شده: %d | موفق: %d' if self.language == 'fa' else 'Shown: %d | Failed: %d | Locked: %d | Successful: %d') % (report['shown'], counts['failure'], counts['locked'], counts['success']))

        def show_event_detail(self, row, _column):
            if not 0 <= row < len(self._events):
                return
            event = self._events[row]
            fa = self.language == 'fa'
            dialog = QDialog(self)
            dialog.setWindowTitle('جزئیات رویداد امنیتی' if fa else 'Security event details')
            dialog.resize(560, 300)
            layout = QVBoxLayout(dialog)
            labels = (('شناسه', 'ID'), ('نام کاربری', 'Username'), ('نتیجه', 'Outcome'), ('زمان UTC', 'UTC timestamp'), ('جزئیات', 'Detail'))
            for key, names in zip(('id','attempted_username','outcome','occurred_at','detail'), labels):
                line = QLabel(f'{names[0] if fa else names[1]}: {event.get(key, )}')
                line.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                line.setWordWrap(True)
                layout.addWidget(line)
            close_btn = QPushButton('بستن' if fa else 'Close')
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            dialog.exec()

        def export_csv(self):
            path, _ = QFileDialog.getSaveFileName(self, self.windowTitle(), 'security-events.csv', 'CSV (*.csv)')
            if not path: return
            try: export_security_events_csv(path, self._events, language=self.language)
            except OSError as exc: QMessageBox.warning(self, self.windowTitle(), str(exc)); return
            QMessageBox.information(self, self.windowTitle(), 'ذخیره شد' if self.language == 'fa' else 'Export completed')
else:
    class SecurityAdminPanel:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('PySide6 is required to display SecurityAdminPanel')
