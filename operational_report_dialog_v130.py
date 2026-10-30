from contextlib import closing
"""Bilingual operational report preview and atomic PDF/Excel exports."""
import os
import sqlite3
import tempfile
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QCheckBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QFileDialog,QMessageBox,QScrollArea,QWidget)
from operation_guard import authorize_action
from operational_reports_v130 import REPORTS,HEADERS,fetch,write_excel,write_pdf

NAMES={'fa':{'reservations':'رزروها','rooms':'اتاق‌ها','guests':'مهمانان','payments':'پرداخت‌ها','expenses':'هزینه‌ها'},
       'en':{'reservations':'Reservations','rooms':'Rooms','guests':'Guests','payments':'Payments','expenses':'Expenses'}}
class OperationalReportDialog(QDialog):
    def __init__(self,db_path,actor_id,token,language='fa',parent=None):
        super().__init__(parent)
        self.db_path=db_path;self.actor_id=actor_id;self.token=token
        self.lang=language if language in HEADERS else 'en';fa=self.lang=='fa'
        self.rows=[];self.last_query=None
        self.setWindowTitle('گزارش‌های عملیاتی هتل' if fa else 'Hotel Operational Reports')
        self.resize(950,680)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        layout=QVBoxLayout(self)
        filters=QHBoxLayout();filters.addWidget(QLabel('گزارش' if fa else 'Report'))
        self.kind=QComboBox()
        for key,label in NAMES[self.lang].items():self.kind.addItem(label,key)
        filters.addWidget(self.kind)
        filters.addWidget(QLabel('روزهای اخیر' if fa else 'Last days'))
        self.days=QSpinBox();self.days.setRange(1,365);self.days.setValue(30);filters.addWidget(self.days)
        layout.addLayout(filters)
        self.fields_container=QWidget();self.fields_row=QHBoxLayout(self.fields_container);layout.addWidget(self.fields_container)
        self.checks={}
        self.table=QTableWidget();self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);layout.addWidget(self.table)
        self.message=QLabel('برای مشاهده گزارش، پیش‌نمایش را انتخاب کنید.' if fa else 'Select Preview to load a report.')
        layout.addWidget(self.message)
        actions=QHBoxLayout();preview=QPushButton('پیش‌نمایش' if fa else 'Preview')
        excel=QPushButton('خروجی Excel' if fa else 'Export Excel');pdf=QPushButton('خروجی PDF' if fa else 'Export PDF')
        for button in (preview,excel,pdf):actions.addWidget(button)
        layout.addLayout(actions)
        self.kind.currentIndexChanged.connect(self.rebuild_fields)
        self.days.valueChanged.connect(self.invalidate)
        preview.clicked.connect(self.preview)
        excel.clicked.connect(lambda:self.export('xlsx'))
        pdf.clicked.connect(lambda:self.export('pdf'))
        self.rebuild_fields()
    def connect(self):
        conn=sqlite3.connect(str(self.db_path),timeout=5)
        try:authorize_action(conn,self.actor_id,self.token,'security.view')
        except BaseException:conn.close();raise
        return conn
    def rebuild_fields(self,*_):
        while self.fields_row.count():
            item=self.fields_row.takeAt(0)
            if item.widget():item.widget().deleteLater()
        self.checks={};spec=REPORTS[self.kind.currentData()]
        for field in spec['columns']:
            check=QCheckBox(HEADERS[self.lang][field]);check.setChecked(field in spec['default'])
            check.toggled.connect(self.invalidate);self.fields_row.addWidget(check);self.checks[field]=check
        self.invalidate()
    def invalidate(self,*_):
        self.last_query=None;self.rows=[]
        self.message.setText('پیش‌نمایش نیاز به به‌روزرسانی دارد' if self.lang=='fa' else 'Preview needs refreshing')
    def selected(self):return tuple(field for field,check in self.checks.items() if check.isChecked())
    def query(self):return (self.kind.currentData(),self.selected(),self.days.value())
    def preview(self):
        try:
            kind,columns,days=self.query()
            with closing(self.connect()) as conn:rows=fetch(conn,self.actor_id,report=kind,columns=columns,days=days)
            self.rows=rows;self.last_query=(kind,columns,days)
            self.table.setColumnCount(len(columns));self.table.setHorizontalHeaderLabels([HEADERS[self.lang][c] for c in columns]);self.table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):self.table.setItem(i,j,QTableWidgetItem(str(value) if value is not None else '—'))
            self.message.setText(f'{len(rows)} '+('رکورد' if self.lang=='fa' else 'records')+' (max 250)')
            return True
        except (ValueError,PermissionError,sqlite3.Error) as exc:
            QMessageBox.warning(self,'Report',str(exc));return False
    def export(self,fmt):
        if self.last_query!=self.query() and not self.preview():return
        filename,_=QFileDialog.getSaveFileName(self,'Export',f'hotel_{self.kind.currentData()}.{fmt}',
            'Excel (*.xlsx)' if fmt=='xlsx' else 'PDF (*.pdf)')
        if not filename:return
        if not filename.lower().endswith('.'+fmt):filename+='.'+fmt
        temp=None
        try:
            # Re-authorize at the point of export.
            with closing(self.connect()):pass
            fd,temp=tempfile.mkstemp(prefix='.hotel-report-',suffix='.'+fmt,dir=str(Path(filename).parent))
            os.close(fd)
            if fmt=='xlsx':write_excel(temp,self.last_query[1],self.rows,self.lang)
            else:write_pdf(temp,self.last_query[1],self.rows,self.lang)
            os.replace(temp,filename);temp=None
            self.message.setText('گزارش ذخیره شد' if self.lang=='fa' else 'Report saved')
        except (OSError,ValueError,PermissionError,sqlite3.Error,RuntimeError,ImportError) as exc:
            QMessageBox.warning(self,'Report',str(exc))
        finally:
            if temp is not None:
                try:os.unlink(temp)
                except OSError:pass
