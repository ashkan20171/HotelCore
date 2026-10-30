"""Jalali calendar conversion and a reusable PySide6 date picker."""
from datetime import date
import jdatetime


def jalali_from_iso(iso_date):
    return jdatetime.date.fromgregorian(date=date.fromisoformat(iso_date))


def iso_from_jalali(year, month, day):
    """Validate a Jalali date and return Gregorian ISO-8601 for SQLite."""
    return jdatetime.date(int(year), int(month), int(day)).togregorian().isoformat()


def jalali_month_days(year, month):
    """Return the number of days in a Jalali month, including leap Esfand."""
    for day in range(31, 27, -1):
        try:
            jdatetime.date(int(year), int(month), day)
            return day
        except ValueError:
            pass
    raise ValueError('Invalid Jalali year or month')


def choose_jalali_date(parent, current_iso, language='fa'):
    """Show modal Jalali picker. Return ISO date or None on cancellation."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox
    current = jalali_from_iso(current_iso)
    dialog = QDialog(parent)
    dialog.setWindowTitle('انتخاب تاریخ شمسی' if language == 'fa' else 'Select Jalali date')
    dialog.setMinimumWidth(350)
    dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == 'fa' else Qt.LayoutDirection.LeftToRight)
    root = QVBoxLayout(dialog)
    hint = QLabel('سال / ماه / روز' if language == 'fa' else 'Year / Month / Day')
    root.addWidget(hint)
    fields = QHBoxLayout()
    year, month, day = QSpinBox(), QSpinBox(), QSpinBox()
    year.setRange(1200, 1700);year.setValue(current.year)
    month.setRange(1, 12);month.setValue(current.month)
    day.setRange(1, 31);day.setValue(current.day)
    for field in (year, month, day):fields.addWidget(field)
    root.addLayout(fields)
    def update_days():
        day.setMaximum(jalali_month_days(year.value(), month.value()))
    year.valueChanged.connect(update_days)
    month.valueChanged.connect(update_days)
    update_days()
    actions = QHBoxLayout()
    ok = QPushButton('تأیید' if language == 'fa' else 'Confirm')
    cancel = QPushButton('انصراف' if language == 'fa' else 'Cancel')
    ok.clicked.connect(dialog.accept);cancel.clicked.connect(dialog.reject)
    actions.addWidget(ok);actions.addWidget(cancel);root.addLayout(actions)
    if dialog.exec() != QDialog.DialogCode.Accepted:return None
    try:return iso_from_jalali(year.value(),month.value(),day.value())
    except ValueError:
        QMessageBox.warning(parent,dialog.windowTitle(),'تاریخ نامعتبر است' if language=='fa' else 'Invalid date')
        return None
