"""PySide6 dialog for browsing reservation audit events (Stage 162)."""
from __future__ import annotations
import json
import sqlite3
from PySide6.QtCore import Qt, QDate
from booking_audit_export_v163 import export_events_csv
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QTextBrowser, QHeaderView, QMessageBox, QAbstractItemView, QFileDialog)

class BookingAuditDialog(QDialog):
    def __init__(self, connection_factory, language='fa', parent=None):
        super().__init__(parent)
        self.connection_factory = connection_factory
        self.language = language if language in ('fa', 'en') else 'fa'
        fa = self.language == 'fa'
        self.setWindowTitle('تاریخچه تغییرات رزرو' if fa else 'Reservation Audit Timeline')
        self.resize(1000, 650)
        self.setMinimumSize(760, 480)
        root = QVBoxLayout(self)
        filters = QHBoxLayout()
        self.reservation_id = QLineEdit()
        self.reservation_id.setPlaceholderText('شناسه رزرو (اختیاری)' if fa else 'Reservation ID (optional)')
        self.reservation_id.setMaximumWidth(190)
        self.event_type = QComboBox()
        self.event_type.addItem('همه رویدادها' if fa else 'All events', '')
        for key, fa_label, en_label in [('created','ایجاد','Created'),('updated','ویرایش','Updated'),('deleted','حذف','Deleted')]:
            self.event_type.addItem(fa_label if fa else en_label, key)
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filters.addWidget(self.reservation_id)
        filters.addWidget(QLabel('رویداد' if fa else 'Event'))
        filters.addWidget(self.event_type)
        filters.addWidget(QLabel('از' if fa else 'From'))
        filters.addWidget(self.start_date)
        filters.addWidget(QLabel('تا' if fa else 'To'))
        filters.addWidget(self.end_date)
        self.search_button = QPushButton('اعمال فیلتر' if fa else 'Apply filters')
        self.search_button.clicked.connect(self.reload)
        filters.addWidget(self.search_button)
        self.export_button = QPushButton('خروجی CSV' if fa else 'Export CSV')
        self.export_button.clicked.connect(self.export_csv)
        filters.addWidget(self.export_button)
        root.addLayout(filters)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['شناسه رویداد','شناسه رزرو','نوع رویداد','زمان (UTC)','عامل ثبت'] if fa else ['Event ID','Reservation ID','Event','Time (UTC)','Actor'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.show_details)
        root.addWidget(self.table, 3)
        root.addWidget(QLabel('جزئیات قبل و بعد از تغییر' if fa else 'Before / after details'))
        self.details = QTextBrowser()
        self.details.setOpenExternalLinks(False)
        root.addWidget(self.details, 2)
        bottom = QHBoxLayout()
        self.status = QLabel()
        bottom.addWidget(self.status, 1)
        close = QPushButton('بستن' if fa else 'Close')
        close.clicked.connect(self.accept)
        bottom.addWidget(close)
        root.addLayout(bottom)
        self.events = []
        self.reload()

    def reload(self):
        fa = self.language == 'fa'
        raw_id = self.reservation_id.text().strip()
        if raw_id and (not raw_id.isascii() or not raw_id.isdigit() or int(raw_id) < 1):
            QMessageBox.warning(self, 'ورودی نامعتبر' if fa else 'Invalid input',
                                'شناسه رزرو باید عدد صحیح مثبت باشد.' if fa else 'Reservation ID must be a positive integer.')
            return
        if self.start_date.date() > self.end_date.date():
            QMessageBox.warning(self, 'بازه نامعتبر' if fa else 'Invalid range',
                                'تاریخ شروع نباید بعد از تاریخ پایان باشد.' if fa else 'Start date must not be after end date.')
            return
        clauses = ['date(event_at) BETWEEN date(?) AND date(?)']
        params = [self.start_date.date().toString('yyyy-MM-dd'), self.end_date.date().toString('yyyy-MM-dd')]
        if raw_id:
            clauses.append('reservation_id=?'); params.append(int(raw_id))
        if self.event_type.currentData():
            clauses.append('event_type=?'); params.append(self.event_type.currentData())
        try:
            with self.connection_factory() as conn:
                rows = conn.execute('''SELECT id,reservation_id,event_type,event_at,actor,old_values,new_values
                    FROM booking_audit_events WHERE ''' + ' AND '.join(clauses) + ' ORDER BY event_at DESC,id DESC LIMIT 500', params).fetchall()
        except sqlite3.Error as exc:
            QMessageBox.critical(self, 'خطای پایگاه داده' if fa else 'Database error', str(exc))
            return
        self.events = []
        self.table.setRowCount(0)
        labels = {'created': 'ایجاد' if fa else 'Created', 'updated': 'ویرایش' if fa else 'Updated', 'deleted': 'حذف' if fa else 'Deleted'}
        for row in rows:
            event = dict(zip(('id','reservation_id','event_type','event_at','actor','old_values','new_values'), row))
            self.events.append(event)
            index = self.table.rowCount(); self.table.insertRow(index)
            values = (event['id'], event['reservation_id'], labels.get(event['event_type'], event['event_type']), event['event_at'], event['actor'])
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.table.setItem(index, col, item)
        self.status.setText((f'{len(rows)} رویداد (حداکثر ۵۰۰)' if fa else f'{len(rows)} events (max 500)'))
        self.details.clear()
        if rows:
            self.table.selectRow(0)

    def show_details(self):
        selected = self.table.selectedItems()
        if not selected:
            self.details.clear(); return
        index = selected[0].data(Qt.ItemDataRole.UserRole)
        if index is None or not 0 <= index < len(self.events):
            self.details.clear(); return
        event = self.events[index]
        fa = self.language == 'fa'
        payload = {'event_id': event['id'], 'reservation_id': event['reservation_id'],
                   'event_type': event['event_type'], 'event_at_utc': event['event_at'],
                   'actor': event['actor'],
                   ('مقادیر قبلی' if fa else 'before'): self._json_value(event['old_values']),
                   ('مقادیر جدید' if fa else 'after'): self._json_value(event['new_values'])}
        self.details.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2))

    @staticmethod
    def _json_value(value):
        if value is None: return None
        if isinstance(value, (dict, list)): return value
        try: return json.loads(value)
        except (ValueError, TypeError): return value

    def export_csv(self):
        """Export exactly the events currently displayed after applying filters."""
        fa = self.language == 'fa'
        title = 'ذخیره تاریخچه رزرو' if fa else 'Export reservation audit'
        path, _ = QFileDialog.getSaveFileName(self, title, 'reservation-audit.csv', 'CSV (*.csv)')
        if not path:
            return
        if not path.lower().endswith('.csv'):
            path += '.csv'
        try:
            count = export_events_csv(path, self.events, self.language)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, 'خطای خروجی' if fa else 'Export error', str(exc))
            return
        QMessageBox.information(self, 'موفق' if fa else 'Success',
            (f'{count} رویداد ذخیره شد.' if fa else f'{count} events exported successfully.'))
