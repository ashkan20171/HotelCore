"""Premium bilingual login screen; UI has no database dependencies."""
from pathlib import Path
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QDialog,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
 QPushButton,QComboBox,QFrame,QCheckBox,QMessageBox,QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor

COPY = {
 'fa': {'window':'ورود امن | Ashkan Hotel Pro','heading':'به اشکان هتل خوش آمدید',
 'tagline':'سامانه حرفه‌ای مدیریت هتل و شعب','username':'نام کاربری','password':'رمز عبور',
 'login':'ورود به داشبورد','show':'نمایش رمز عبور','error':'نام کاربری یا رمز عبور اشتباه است.',
 'error_title':'ورود ناموفق','hint':'مدیریت هوشمند اقامت • تجربه‌ای متفاوت','required':'نام کاربری و رمز عبور را وارد کنید.'},
 'en': {'window':'Secure sign in | Ashkan Hotel Pro','heading':'Welcome to Ashkan Hotel',
 'tagline':'Professional hotel and branch management','username':'Username','password':'Password',
 'login':'Sign in to dashboard','show':'Show password','error':'Invalid username or password.',
 'error_title':'Sign-in failed','hint':'Smarter hospitality • Seamless experience','required':'Enter your username and password.'}
}

class PremiumLoginDialog(QDialog):
 def __init__(self, authenticate, parent=None):
  super().__init__(parent)
  self.authenticate=authenticate
  self.role=None;self.user_id=None;self.username_value=None
  self.settings=QSettings('AshkanHotelPro','HotelPMS')
  self.language=self.settings.value('ui/language','fa')
  if self.language not in COPY:self.language='fa'
  self.setObjectName('loginWindow');self.setMinimumSize(520,590);self.resize(590,680)
  self.setStyleSheet("""
  QDialog#loginWindow {background:#091827;color:#e8f4ff;font-family:Tahoma;}
  QFrame#loginCard {background:#132b42;border:1px solid #31516b;border-radius:24px;}
  QLabel#brand {font-size:23px;font-weight:800;color:#f4d99b;}
  QLabel#heading {font-size:22px;font-weight:800;color:#f2f8ff;}
  QLabel#tagline {font-size:13px;color:#a6bfd0;}
  QLabel#hint {font-size:12px;color:#8aafbc;}
  QLineEdit {background:#0e2135;color:#f4fbff;border:1px solid #426078;border-radius:11px;padding:13px;font-size:14px;}
  QLineEdit:focus {border:2px solid #20c5b6;}
  QComboBox:focus, QPushButton:focus {border:2px solid #f4d99b;}
  QPushButton#signIn {background:#0b9b92;color:white;border:0;border-radius:12px;padding:15px;font-size:15px;font-weight:bold;}
  QPushButton#signIn:hover {background:#0fb5aa;}
  QPushButton#signIn:disabled {background:#4d6974;}
  QComboBox {background:#17324b;color:#fff;border:1px solid #49647b;border-radius:9px;padding:8px;min-width:110px;}
  QCheckBox {color:#bad2de;spacing:9px;}
  QLabel#error {color:#ffb0b0;font-size:12px;}
  """)
  outer=QVBoxLayout(self);outer.setContentsMargins(26,24,26,22);outer.setSpacing(15)
  top=QHBoxLayout();top.addStretch()
  self.lang=QComboBox();self.lang.addItem('فارسی','fa');self.lang.addItem('English','en');self.lang.setCurrentIndex(1 if self.language=='en' else 0)
  self.lang.currentIndexChanged.connect(self.set_language);top.addWidget(self.lang);outer.addLayout(top)
  card=QFrame();card.setObjectName('loginCard');shadow=QGraphicsDropShadowEffect(card);shadow.setBlurRadius(35);shadow.setOffset(0,12);shadow.setColor(QColor(0,0,0,100));card.setGraphicsEffect(shadow)
  inner=QVBoxLayout(card);inner.setContentsMargins(30,24,30,28);inner.setSpacing(14)
  self.logo=QLabel();self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter);self.logo.setFixedHeight(116)
  renderer=QSvgRenderer(str(Path(__file__).with_name('assets')/'hotel_logo.svg'))
  image=QPixmap(126,126);image.fill(Qt.GlobalColor.transparent);p=QPainter(image);renderer.render(p);p.end();self.logo.setPixmap(image)
  inner.addWidget(self.logo)
  brand=QLabel('ASHKAN HOTEL PRO');brand.setObjectName('brand');brand.setAlignment(Qt.AlignmentFlag.AlignCenter);inner.addWidget(brand)
  self.heading=QLabel();self.heading.setObjectName('heading');self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter);inner.addWidget(self.heading)
  self.tagline=QLabel();self.tagline.setObjectName('tagline');self.tagline.setAlignment(Qt.AlignmentFlag.AlignCenter);self.tagline.setWordWrap(True);inner.addWidget(self.tagline)
  inner.addSpacing(16)
  self.username=QLineEdit();self.username.setClearButtonEnabled(True);self.username.setAccessibleName('Username');inner.addWidget(self.username)
  self.password=QLineEdit();self.password.setEchoMode(QLineEdit.EchoMode.Password);self.password.setAccessibleName('Password');inner.addWidget(self.password)
  self.show_password=QCheckBox();self.show_password.toggled.connect(self.toggle_password);inner.addWidget(self.show_password)
  self.error=QLabel('');self.error.setObjectName('error');self.error.setWordWrap(True);self.error.setMinimumHeight(24);inner.addWidget(self.error)
  self.submit=QPushButton();self.submit.setObjectName('signIn');self.submit.clicked.connect(self.login);inner.addWidget(self.submit)
  inner.addStretch();outer.addWidget(card,1)
  self.hint=QLabel();self.hint.setObjectName('hint');self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter);outer.addWidget(self.hint)
  self.password.returnPressed.connect(self.login);self.username.returnPressed.connect(self.password.setFocus)
  self.set_language();self.username.setFocus()
 def toggle_password(self,checked):
  self.password.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
 def set_language(self,*_):
  self.language=self.lang.currentData() or 'fa';self.settings.setValue('ui/language',self.language)
  self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language=='fa' else Qt.LayoutDirection.LeftToRight)
  self.username.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
  self.password.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
  c=COPY[self.language];self.setWindowTitle(c['window']);self.heading.setText(c['heading']);self.tagline.setText(c['tagline'])
  self.username.setPlaceholderText(c['username']);self.password.setPlaceholderText(c['password']);self.show_password.setText(c['show'])
  self.submit.setText(c['login']);self.hint.setText(c['hint']);self.error.clear()
 def login(self):
  c=COPY[self.language];username=self.username.text().strip();password=self.password.text()
  if not username or not password:self.error.setText(c['required']);return
  self.submit.setEnabled(False)
  try:
   result=self.authenticate(username,password)
  except Exception:
   self.error.setText(c['error']);self.submit.setEnabled(True);return
  self.submit.setEnabled(True)
  if result:
   self.role,self.user_id=result;self.username_value=username;self.password.clear();self.accept()
  else:
   self.error.setText(c['error']);self.password.clear();self.password.setFocus()
