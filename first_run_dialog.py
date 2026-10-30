"""Bilingual first-run wizard for local administrator setup."""
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from first_run_security import create_first_admin

class FirstRunDialog(QDialog):
    def __init__(self, connection_factory, parent=None):
        super().__init__(parent)
        self.connection_factory=connection_factory
        language=QSettings('AshkanHotelPro','HotelPMS').value('ui/language','fa')
        fa=language!='en'
        self.setWindowTitle('راه‌اندازی امن مدیر اولیه' if fa else 'Secure administrator setup')
        self.setMinimumWidth(460)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        layout=QVBoxLayout(self)
        heading=QLabel('حساب مدیر را با رمز اختصاصی بسازید' if fa else 'Create your administrator account')
        heading.setWordWrap(True);layout.addWidget(heading)
        self.username=QLineEdit();self.username.setPlaceholderText('نام کاربری' if fa else 'Username')
        self.password=QLineEdit();self.password.setPlaceholderText('رمز عبور قوی' if fa else 'Strong password')
        self.confirm=QLineEdit();self.confirm.setPlaceholderText('تکرار رمز عبور' if fa else 'Confirm password')
        for field in (self.password,self.confirm):
            field.setEchoMode(QLineEdit.EchoMode.Password)
            field.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.username.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        for field in (self.username,self.password,self.confirm):layout.addWidget(field)
        self.show=QCheckBox('نمایش رمزها' if fa else 'Show passwords')
        self.show.toggled.connect(self.toggle);layout.addWidget(self.show)
        hint=QLabel('حداقل ۱۲ نویسه؛ حروف بزرگ و کوچک انگلیسی، عدد و نماد' if fa else
                    'At least 12 characters, uppercase, lowercase, digit and symbol')
        hint.setWordWrap(True);layout.addWidget(hint)
        self.error=QLabel();self.error.setWordWrap(True)
        self.error.setStyleSheet('color:#ffb3ad');layout.addWidget(self.error)
        submit=QPushButton('ساخت حساب مدیر' if fa else 'Create administrator')
        submit.setObjectName('primary');submit.clicked.connect(self.create);layout.addWidget(submit)
    def toggle(self, checked):
        mode=QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.password.setEchoMode(mode);self.confirm.setEchoMode(mode)
    def create(self):
        try:
            with self.connection_factory() as conn:
                create_first_admin(conn,self.username.text(),self.password.text(),self.confirm.text())
        except Exception as exc:
            self.error.setText(str(exc))
            return
        self.password.clear();self.confirm.clear();self.accept()
