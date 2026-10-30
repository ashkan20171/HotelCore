# Bilingual custom report builder dialog
import os
import sqlite3
import tempfile
from pathlib import Path
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QCheckBox,QSpinBox,
    QComboBox,QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QHeaderView)
from operation_guard import authorize_action
from custom_report_builder_v129 import (FIELDS,HEADERS,fetch_report,save_template,
    list_templates,delete_template,write_excel,write_pdf)

class CustomReportDialog(QDialog):
    def __init__(self, db_path, actor_id, token, language='fa', parent=None):
        super().__init__(parent)
        self.db_path=db_path;self.actor_id=actor_id;self.token=token
        self.lang=language;self.rows=[];self.preview_columns=()
        fa=language=='fa'
        self.setWindowTitle('گزارش‌ساز سفارشی' if fa else 'Custom Report Builder')
        self.resize(850,650)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel('ستون‌های گزارش' if fa else 'Report columns'))
        columns_row=QHBoxLayout();self.checks=[]
        for field,label in zip(FIELDS,HEADERS[language]):
            check=QCheckBox(label);check.setChecked(True);columns_row.addWidget(check)
            self.checks.append(check)
        layout.addLayout(columns_row)
        filters=QHBoxLayout()
        filters.addWidget(QLabel('روزهای اخیر' if fa else 'Last days'))
        self.days=QSpinBox();self.days.setRange(1,365);self.days.setValue(30);filters.addWidget(self.days)
        self.status=QComboBox()
        for label,value in ((('همه','all'),('سالم','ok'),('هشدار','warning')) if fa else
                            (('All','all'),('Healthy','ok'),('Warnings','warning'))):
            self.status.addItem(label,value)
        filters.addWidget(self.status);layout.addLayout(filters)
        presets=QHBoxLayout();self.name=QLineEdit();self.name.setPlaceholderText('نام قالب' if fa else 'Template name')
        self.templates=QComboBox()
        save=QPushButton('ذخیره قالب' if fa else 'Save template')
        apply=QPushButton('اعمال قالب' if fa else 'Apply template')
        delete=QPushButton('حذف قالب' if fa else 'Delete template')
        for w in (self.name,self.templates,save,apply,delete):presets.addWidget(w)
        layout.addLayout(presets)
        self.table=QTableWidget(0,4);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.message=QLabel('برای مشاهده گزارش، پیش‌نمایش را انتخاب کنید.' if fa else 'Select Preview to view your report.')
        layout.addWidget(self.message)
        buttons=QHBoxLayout();preview=QPushButton('پیش‌نمایش' if fa else 'Preview')
        excel=QPushButton('Excel');pdf=QPushButton('PDF')
        for w in (preview,excel,pdf):buttons.addWidget(w)
        layout.addLayout(buttons)
        preview.clicked.connect(self.preview)
        excel.clicked.connect(lambda:self.export('xlsx'))
        pdf.clicked.connect(lambda:self.export('pdf'))
        save.clicked.connect(self.save)
        apply.clicked.connect(self.apply)
        delete.clicked.connect(self.delete)
        for check in self.checks:check.toggled.connect(self.invalidate)
        self.days.valueChanged.connect(self.invalidate);self.status.currentIndexChanged.connect(self.invalidate)
        self.reload_templates()
    def conn(self):
        conn=sqlite3.connect(self.db_path,timeout=5)
        try:authorize_action(conn,self.actor_id,self.token,'security.view')
        except BaseException:conn.close();raise
        return conn
    def columns(self):return tuple(field for field,check in zip(FIELDS,self.checks) if check.isChecked())
    def invalidate(self,*_):
        self.rows=[];self.preview_columns=()
        self.message.setText('پیش‌نمایش نیاز به به‌روزرسانی دارد' if self.lang=='fa' else 'Preview needs refreshing')
    def reload_templates(self):
        try:
            with self.conn() as conn: items=list_templates(conn,self.actor_id)
            self.templates.clear()
            for name,columns,days,status in items:self.templates.addItem(name,(columns,days,status))
        except (ValueError,PermissionError,sqlite3.Error) as exc:self.error(exc)
    def error(self,exc):QMessageBox.warning(self,'Report Builder',str(exc))
    def save(self):
        try:
            with self.conn() as conn:save_template(conn,self.actor_id,self.name.text().strip(),self.columns(),self.days.value(),self.status.currentData())
            self.reload_templates()
        except (ValueError,PermissionError,sqlite3.Error) as exc:self.error(exc)
    def apply(self):
        data=self.templates.currentData()
        if data is None:return
        columns,days,status=data
        for field,check in zip(FIELDS,self.checks):check.setChecked(field in columns)
        self.days.setValue(days);self.status.setCurrentIndex(self.status.findData(status))
        self.invalidate()
    def delete(self):
        name=self.templates.currentText()
        if not name:return
        try:
            with self.conn() as conn:delete_template(conn,self.actor_id,name)
            self.reload_templates()
        except (ValueError,PermissionError,sqlite3.Error) as exc:self.error(exc)
    def preview(self):
        try:
            columns=self.columns()
            with self.conn() as conn:rows=fetch_report(conn,self.actor_id,columns=columns,days=self.days.value(),status=self.status.currentData())
            self.rows=rows;self.preview_columns=columns
            self.table.setColumnCount(len(columns));self.table.setHorizontalHeaderLabels([HEADERS[self.lang][FIELDS.index(c)] for c in columns])
            self.table.setRowCount(len(rows))
            for i,row in enumerate(rows):
                for j,value in enumerate(row):self.table.setItem(i,j,QTableWidgetItem(str(value)))
            self.message.setText((f'{len(rows)} رکورد' if self.lang=='fa' else f'{len(rows)} records')+' (max 250)')
        except (ValueError,PermissionError,sqlite3.Error) as exc:self.error(exc)
    def export(self,fmt):
        if not self.preview_columns or self.preview_columns!=self.columns():
            self.preview()
            if not self.preview_columns:return
        filename,_=QFileDialog.getSaveFileName(self,'Export',f'custom_health_report.{fmt}',
                'Excel (*.xlsx)' if fmt=='xlsx' else 'PDF (*.pdf)')
        if not filename:return
        if not filename.lower().endswith('.'+fmt):filename+='.'+fmt
        tmp=None
        try:
            # Check session again before writing; no DB changes occur during export.
            with self.conn() as conn:pass
            parent=Path(filename).parent
            fd,tmp=tempfile.mkstemp(prefix='.ashkan-report-',suffix='.'+fmt,dir=str(parent))
            os.close(fd)
            if fmt=='xlsx':write_excel(tmp,self.preview_columns,self.rows,self.lang)
            else:write_pdf(tmp,self.preview_columns,self.rows,self.lang)
            os.replace(tmp,filename);tmp=None
            self.message.setText('گزارش ذخیره شد' if self.lang=='fa' else 'Report saved')
        except (OSError,ValueError,RuntimeError,PermissionError,sqlite3.Error,ImportError) as exc:self.error(exc)
        finally:
            if tmp is not None:
                try:os.unlink(tmp)
                except OSError:pass
