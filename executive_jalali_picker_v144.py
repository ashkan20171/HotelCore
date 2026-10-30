"""Accessible Saturday-first Jalali month grid with keyboard navigation."""
from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QMessageBox,QGridLayout,QComboBox,QSpinBox,QWidget
from executive_jalali_v143 import jalali_label,parse_jalali
from executive_calendar_grid_v145 import month_grid,adjacent_month

class JalaliDatePicker(QDialog):
    MONTHS=('فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند')
    DAYS=('ش','ی','د','س','چ','پ','ج')
    def __init__(self,initial=None,parent=None):
        super().__init__(parent)
        self.setWindowTitle('تقویم شمسی | انتخاب تاریخ')
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(360)
        self.selected=None
        parts=jalali_label(initial or date.today()).split('/')
        self.year_value=int(parts[0]);self.month_value=int(parts[1]);self.day_value=int(parts[2])
        layout=QVBoxLayout(self)
        nav=QHBoxLayout();layout.addLayout(nav)
        previous=QPushButton('ماه قبل');next_button=QPushButton('ماه بعد')
        self.year=QSpinBox();self.year.setRange(1200,1600);self.year.setValue(self.year_value)
        self.month=QComboBox();self.month.addItems(self.MONTHS);self.month.setCurrentIndex(self.month_value-1)
        for widget in (previous,self.month,self.year,next_button):nav.addWidget(widget)
        previous.clicked.connect(lambda:self._shift(-1));next_button.clicked.connect(lambda:self._shift(1))
        self.year.valueChanged.connect(self._controls_changed)
        self.month.currentIndexChanged.connect(self._controls_changed)
        self.calendar=QWidget();self.grid=QGridLayout(self.calendar);self.grid.setSpacing(4)
        layout.addWidget(self.calendar)
        footer=QHBoxLayout();layout.addLayout(footer)
        today=QPushButton('امروز');cancel=QPushButton('انصراف')
        footer.addWidget(today);footer.addWidget(cancel)
        today.clicked.connect(self._today);cancel.clicked.connect(self.reject)
        self.setStyleSheet('QDialog {background:#0B1D2B;color:#F0FAFF;} QLabel{color:#C6E5F1;} QPushButton{background:#17445B;color:white;border:1px solid #36647C;border-radius:6px;padding:7px;} QPushButton:hover{background:#26718A;} QPushButton:disabled{color:#8194A2;background:#18313D;}')
        self._render()
    def _controls_changed(self,*_):
        self.year_value=self.year.value();self.month_value=self.month.currentIndex()+1
        self._render()
    def _shift(self,offset):
        try:year,month=adjacent_month(self.year_value,self.month_value,offset)
        except ValueError:return
        self.year.blockSignals(True);self.month.blockSignals(True)
        self.year.setValue(year);self.month.setCurrentIndex(month-1)
        self.year.blockSignals(False);self.month.blockSignals(False)
        self.year_value=year;self.month_value=month;self._render()
    def _render(self):
        while self.grid.count():
            item=self.grid.takeAt(0)
            if item.widget():item.widget().deleteLater()
        for col,name in enumerate(self.DAYS):
            heading=QLabel(name);heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(heading,0,col)
        for row,week in enumerate(month_grid(self.year_value,self.month_value),1):
            for col,day in enumerate(week):
                button=QPushButton('' if day is None else str(day))
                button.setEnabled(day is not None)
                button.setAccessibleName(f'{self.year_value}/{self.month_value:02d}/{day:02d}' if day else 'روز خالی')
                if day is not None:
                    button.clicked.connect(lambda checked=False,d=day:self._choose(d))
                    if day==self.day_value:button.setStyleSheet('background:#197D7C;border:2px solid #57E0CC;')
                self.grid.addWidget(button,row,col)
    def _choose(self,day):
        value=f'{self.year_value:04d}/{self.month_value:02d}/{day:02d}'
        try:self.selected=parse_jalali(value)
        except ValueError:
            QMessageBox.warning(self,'تاریخ نامعتبر','تاریخ انتخاب‌شده معتبر نیست');return
        self.accept()
    def _today(self):
        self.selected=date.today();self.accept()
