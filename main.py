import sys, sqlite3, hashlib, secrets, shutil, os, csv, html
from datetime import date, timedelta
from pathlib import Path
import jdatetime
from billing import migrate, calculate_invoice, apply_adjustment
from branches import migrate_branches, add_branch, assign_room
from branch_security import migrate as migrate_branch_security, transfer_room, grant_branch
from branch_reports import branch_summary, branch_reservations
from branch_access import allowed_branches, require_branch, scoped_reservations, scoped_payments, branch_dashboard
from branch_operations import require_room, require_reservation, record_payment, change_reservation_status, grant_user_branch, revoke_user_branch
from branch_guard import authorize_reservation, create_housekeeping, complete_housekeeping, branch_export_rows
from occupancy import build_grid, occupancy_summary
from table_filters import row_matches
from reservation_validation import validate_booking
from form_validation import validate_room, validate_employee, validate_payment, normalize_digits
from guest_search import matches_guest
from reservation_filters import matches_reservation, status_options, status_color
from reservation_service import create_reservation
from booking_audit_v161 import install as install_booking_audit, register_actor_function, set_current_actor
from booking_audit_dialog_v162 import BookingAuditDialog
from password_security import change_password as rotate_password
from pricing import migrate as migrate_pricing, calculate_stay, upcoming_departures, migrate_booking_rates, quote_reservation, save_quote, reschedule
from PySide6.QtCore import Qt, QDate, QSettings, QEvent, QTimer
from localization import translate, NAV_FA, NAV_EN
from navigation_search import matching_navigation_indices
from locale_format import display_date, display_money, jdatetime
from jalali_calendar import choose_jalali_date
from invoice_presentation import render_invoice
from invoice_pdf import write_invoice_pdf
from dashboard_reporting import reporting_window, payment_totals, compare_periods
from branch_csv import export_branch_reservations
from branch_excel import export_branch_workbook
from management_excel import export_management_workbook
from branch_comparison import authorized_comparison, export_comparison_workbook
from stay_performance import estimated_branch_performance, export_estimated_performance
from branch_cashflow import migrate as migrate_branch_cashflow, record_expense, cashflow, export_cashflow
from cashflow_dashboard import cashflow_cards, cashflow_comparison
from cashflow_trends import monthly_cashflow, scale_bars
from cashflow_kpis import compare_cashflow, format_comparison
from cashflow_pdf import write_cashflow_pdf
from finance_chart import CashflowChart
from finance_kpi_cards import FinanceKpiCards
from branch_visuals import comparison_bars
from branch_sorting import sort_branch_rows
from branch_report_filters import filter_branches, comparison_csv
from branch_advanced_filters import filter_financial_rows
from branch_aggregates import visible_totals, totals_caption
from branch_executive_kpis import executive_metrics, executive_labels
from branch_period_insights import previous_interval, branch_period_insights, insight_caption
from branch_alerts import validate_threshold, evaluate_alerts, alert_summary
from branch_alert_priority import categorize_alerts, filter_alerts, priority_label
from branch_comparison_pdf import write_branch_comparison_pdf
from branch_trend_summary import merge_monthly_branches, trend_caption
from branch_trend_excel import export_trend_excel
from branch_trend_chart import BranchTrendChart
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QKeySequence, QShortcut, QLinearGradient
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QLineEdit,QComboBox,QCheckBox,QDateEdit,QMessageBox,QDialog,QFormLayout,QSpinBox,QFrame,QStackedWidget,QHeaderView,QFileDialog,QInputDialog,QTabWidget,QTextBrowser,QCalendarWidget,QProgressBar,QScrollArea,QSizePolicy, QAbstractItemView, QMenu, QGridLayout)

DB=Path(__file__).with_name('hotel.db')
def connect():
    c=sqlite3.connect(DB); c.execute('PRAGMA foreign_keys=ON'); register_actor_function(c); return c
def init():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY,number TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,rate INTEGER NOT NULL,status TEXT DEFAULT 'فعال');
        CREATE TABLE IF NOT EXISTS guests(id INTEGER PRIMARY KEY,name TEXT NOT NULL,phone TEXT NOT NULL,national_id TEXT);
        CREATE TABLE IF NOT EXISTS reservations(id INTEGER PRIMARY KEY,room_id INTEGER NOT NULL REFERENCES rooms(id),guest_id INTEGER NOT NULL REFERENCES guests(id),checkin TEXT NOT NULL,checkout TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'رزرو شده',created_at TEXT DEFAULT CURRENT_TIMESTAMP,CHECK(checkout>checkin));
        CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY,reservation_id INTEGER NOT NULL REFERENCES reservations(id),amount INTEGER NOT NULL CHECK(amount>0),method TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_res_room_dates ON reservations(room_id,checkin,checkout);''')
        c.executescript("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,salt TEXT NOT NULL,role TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS housekeeping(id INTEGER PRIMARY KEY,room_id INTEGER NOT NULL REFERENCES rooms(id),task TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'در انتظار',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_housekeeping_room ON housekeeping(room_id);""")
        c.executescript("""CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY,category TEXT NOT NULL,description TEXT NOT NULL,amount INTEGER NOT NULL CHECK(amount>0),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY,full_name TEXT NOT NULL,position TEXT NOT NULL,phone TEXT NOT NULL,salary INTEGER NOT NULL DEFAULT 0 CHECK(salary>=0),active INTEGER NOT NULL DEFAULT 1);
        CREATE INDEX IF NOT EXISTS idx_expenses_created ON expenses(created_at);""")
        c.executescript("""CREATE TABLE IF NOT EXISTS menu_items(id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE,price INTEGER NOT NULL CHECK(price>0),active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS service_orders(id INTEGER PRIMARY KEY,reservation_id INTEGER NOT NULL REFERENCES reservations(id),item_id INTEGER NOT NULL REFERENCES menu_items(id),quantity INTEGER NOT NULL CHECK(quantity>0),unit_price INTEGER NOT NULL CHECK(unit_price>0),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE,unit TEXT NOT NULL,quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),minimum INTEGER NOT NULL DEFAULT 0 CHECK(minimum>=0));
        CREATE INDEX IF NOT EXISTS idx_orders_reservation ON service_orders(reservation_id);""")
        c.executescript("""CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY, username TEXT NOT NULL, action TEXT NOT NULL, details TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);""")
        c.executescript("""CREATE TABLE IF NOT EXISTS discounts(id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, percent INTEGER NOT NULL CHECK(percent BETWEEN 1 AND 100), active INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP);""")
        migrate_login_security(c)
        from user_access_management import migrate as migrate_user_access
        migrate_user_access(c)
        from permission_policy import migrate as migrate_permissions
        migrate_permissions(c)
        from security_sessions import migrate as migrate_sessions
        migrate_sessions(c)
        migrate_branches(c)
        migrate_branch_security(c)
        migrate(c)
        migrate_pricing(c)
        migrate_booking_rates(c)
        install_booking_audit(c)
        migrate_branch_cashflow(c)
        if not c.execute('SELECT 1 FROM menu_items LIMIT 1').fetchone():
            c.executemany('INSERT INTO menu_items(name,price) VALUES(?,?)',[('صبحانه ایرانی',250000),('ناهار روز',480000),('چای و پذیرایی',95000),('سرویس اتاق',150000)])
        if not c.execute('SELECT 1 FROM rooms LIMIT 1').fetchone():
            c.executemany('INSERT INTO rooms(number,kind,rate) VALUES(?,?,?)',[(str(100+i),'استاندارد' if i<7 else 'سوئیت',1800000 if i<7 else 3900000) for i in range(1,11)])
def audit(username, action, details=''):
    with connect() as c:c.execute('INSERT INTO audit_log(username,action,details) VALUES(?,?,?)',(username,action,details))
def money(n):return f'{n:,} تومان'
def jalali(s):
    try:return jdatetime.date.fromgregorian(date=date.fromisoformat(s)).strftime('%Y/%m/%d')
    except:return s
STYLE="""
QWidget { background:#0a1424; color:#eaf2ff; font-family:Tahoma, "Segoe UI"; font-size:12px; }
QMainWindow { background:#0a1424; }
QFrame#side { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #142842,stop:1 #0e1d32); border:1px solid #29435f; border-radius:22px; }
QLabel#versionLabel { color:#7fa1bc; font-size:10px; padding:8px 4px; }
QLabel#navGroupHeader { color:#91b6c9; font-size:11px; font-weight:700; padding:14px 9px 4px 9px; background:transparent; }
QLabel#brandTitle { color:#f2f8ff; font-size:14px; font-weight:800; padding:4px; }
QLabel#sectionTitle { color:#d8eaf7; font-size:14px; font-weight:700; padding:8px 2px; }
QScrollArea#navScroll, QScrollArea#pageScroll { background:transparent; border:0; }
QPushButton#navButton { text-align:left; padding:9px 12px; min-height:20px; border-radius:10px; font-weight:500; }
QPushButton#navButton:hover { background:#203e59; border-color:#36cbbb; }
QPushButton#navButton[active="true"] { background:#164b58; border:1px solid #25bdae; border-left:4px solid #e5bf75; border-right:4px solid #e5bf75; font-weight:bold; color:#ffffff; }
QPushButton { background:#192e47; color:#eaf2ff; border:1px solid #304a68; border-radius:12px; padding:11px 14px; min-height:18px; }
QPushButton:hover { background:#244562; border-color:#22c7b7; }
QPushButton:focus { border:2px solid #31d3c2; }
QPushButton#primary { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #078e87,stop:1 #0871a0); border:1px solid #27c8b8; color:white; font-weight:bold; }
QPushButton#primary:hover { background:#0aa99e; }
QPushButton#navActive { background:#164b58; border:1px solid #25bdae; border-left:4px solid #e5bf75; border-right:4px solid #e5bf75; font-weight:bold; color:#ffffff; }
QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QSpinBox:focus { border:2px solid #2bd0bf; }
QToolTip { color:#f6f2e9; background:#203751; border:1px solid #c4a66c; padding:7px; border-radius:6px; }
QLabel#fieldError { color:#ffb3ad; background:#4a202b; border:1px solid #a84b58; border-radius:8px; padding:9px; }
QComboBox[invalid="true"], QSpinBox[invalid="true"] { border:2px solid #e77b81; }
QTableWidget::item:selected { background:#176b73; color:white; }
QTableWidget::item:hover { background:#214660; }
QMenu { background:#182b42; color:#f4f8ff; border:1px solid #36516f; padding:7px; }
QMenu::item { padding:9px 16px; border-radius:5px; }
QMenu::item:selected { background:#087e79; }
QPushButton:disabled { color:#8293a7; background:#17263a; border-color:#27384a; }
QLabel#title { font-size:23px; font-weight:bold; color:#f2f8ff; padding:8px 0 10px 0; }
QLabel#subtitle { color:#a5c0d5; font-size:13px; padding:5px 0 13px 0; }
QPushButton#quickAction { background:#19374b; border:1px solid #316678; font-weight:bold; }
QFrame#dashboardCard { background:#172c44; border:1px solid #34506c; border-radius:16px; }
QFrame#dashboardCard:hover { border:1px solid #2cc9b7; background:#1b3650; }
QLabel#dashboardCardLabel { background:transparent; border:0; color:#a9c6d9; font-size:12px; }
QLabel#dashboardCardValue { background:transparent; border:0; color:#f3f9ff; font-size:20px; font-weight:700; }
QLabel#metric { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #19344e,stop:1 #14263d); border:1px solid #2a4966; border-radius:17px; padding:20px; font-size:16px; }
QTableWidget { background:#10243a; alternate-background-color:#162b43; gridline-color:#29415b; border:1px solid #30475f; border-radius:13px; selection-background-color:#176b73; padding:5px; }
QHeaderView::section { background:#1b3551; color:#dff4fa; padding:11px; border:0; font-weight:bold; }
QLineEdit,QComboBox,QDateEdit,QSpinBox { background:#142a43; border:1px solid #36516f; border-radius:10px; padding:10px; color:white; min-height:18px; }
QLineEdit[invalid="true"],QComboBox[invalid="true"],QDateEdit[invalid="true"] { border:2px solid #f87171; background:#392337; }
QScrollArea { border:0; background:transparent; }
QScrollBar:vertical { background:#101e31; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:#315574; border-radius:5px; min-height:25px; }
QScrollBar::handle:vertical:hover { background:#3f7896; }
QStatusBar { background:#11243a; color:#bcd1df; border-top:1px solid #263e58; }
QProgressBar { background:#142a43; border:1px solid #36516f; border-radius:7px; text-align:center; }
QProgressBar::chunk { background:#13a99e; border-radius:6px; }
QTabWidget::pane { border:1px solid #2a4966; border-radius:12px; padding:8px; }
QTabBar::tab { background:#172c44; color:#bcd1df; padding:10px 18px; margin:3px; border-radius:8px; }
QTabBar::tab:selected { background:#087e79; color:white; }
"""
class RevenueChart(QWidget):
  """Lightweight revenue chart with a localized empty state."""
  def __init__(self, points, language='fa', parent=None):
   super().__init__(parent)
   self.points=list(points or [])
   self.language=language
   self.setMinimumHeight(190)
   self.setMaximumHeight(250)
   self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
  def paintEvent(self,event):
   p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
   if not self.points:
    p.setPen(QColor('#8fa8bf'))
    message='No payment data for this period' if self.language=='en' else 'برای این بازه هنوز پرداختی ثبت نشده است'
    p.drawText(self.rect().adjusted(20,10,-20,-10),Qt.AlignmentFlag.AlignCenter,message)
    p.end();return
   rect=self.rect().adjusted(45,20,-20,-35);p.setPen(QPen(QColor('#2a4058'),1))
   for i in range(5):
    y=rect.top()+i*rect.height()/4;p.drawLine(rect.left(),int(y),rect.right(),int(y))
   values=[max(0,float(v or 0)) for _,v in self.points];top=max(values+[1.0]);n=len(values);width=rect.width()/max(1,n)
   for i,(label,val) in enumerate(self.points):
    val=max(0,float(val or 0));h=max(1,int(val/top*(rect.height()-10))) if val>0 else 0
    x=int(rect.left()+i*width+width*.2);y=int(rect.bottom()-h)
    if h:
     gradient=QLinearGradient(x,y,x,rect.bottom());gradient.setColorAt(0,QColor('#35d4c4'));gradient.setColorAt(1,QColor('#087e91'));p.fillRect(x,y,max(3,int(width*.6)),h,gradient)
    p.setPen(QColor('#d9e9f8'));p.drawText(x,int(rect.bottom()+20),str(label)[-7:]);p.setPen(QPen(QColor('#2a4058'),1))
   p.end()
from login_screen import PremiumLoginDialog
from login_security import migrate as migrate_login_security, is_locked, record_failure, clear_failures, record_security_event
from PySide6.QtSvgWidgets import QSvgWidget

def authenticate_user(username, password):
    """Verify credentials with persistent lockout after repeated failed attempts."""
    username=username.strip()
    with connect() as c:
        migrate_login_security(c)
        from security_sessions import migrate as migrate_sessions,record_login
        migrate_sessions(c)
        if is_locked(c,username):
            record_login(c,None,"locked")
            record_security_event(c,username,"locked",detail="lockout_active")
            return None
        row=c.execute('SELECT password_hash,salt,role,id,active FROM users WHERE username=?',(username,)).fetchone()
        # Always run PBKDF2 to reduce username enumeration timing differences.
        salt=bytes.fromhex(row[1]) if row else bytes(16)
        expected=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,240000).hex()
        valid=bool(row and row[4]==1 and secrets.compare_digest(expected,row[0]))
        if not valid:
            record_failure(c,username)
            record_login(c,row[3] if row else None,"failure")
            record_security_event(c,username,"failure",detail="invalid_credentials_or_inactive")
            return None
        clear_failures(c,username)
        role,user_id=row[2],row[3]
        record_login(c,user_id,"success")
        record_security_event(c,username,"success",detail="authenticated")
    audit(username,'login')
    return role,user_id

class LoginDialog(PremiumLoginDialog):
    def __init__(self):
        super().__init__(authenticate_user)

class BookingDialog(QDialog):
 def __init__(self,parent=None):
    super().__init__(parent);self.setWindowTitle('رزرو جدید');self.resize(510,420);f=QFormLayout(self);f.setSpacing(14)
    self.setMinimumWidth(460)
    self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if getattr(parent,'language','fa')=='fa' else Qt.LayoutDirection.LeftToRight)
    self.name=QLineEdit();self.phone=QLineEdit();self.nid=QLineEdit();self.room=QComboBox();self.start=QDateEdit();self.end=QDateEdit()
    self.phone.setLayoutDirection(Qt.LayoutDirection.LeftToRight);self.nid.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    for field in (self.name,self.phone,self.nid):field.setMinimumHeight(36)
    self.name.setMaxLength(100);self.phone.setMaxLength(32);self.nid.setMaxLength(32)
    self.name.setPlaceholderText('نام و نام خانوادگی' if getattr(parent,'language','fa')=='fa' else 'Full name')
    self.phone.setPlaceholderText('شماره تماس' if getattr(parent,'language','fa')=='fa' else 'Phone number')
    for w in (self.start,self.end):w.setCalendarPopup(True);w.setDisplayFormat('yyyy-MM-dd')
    from PySide6.QtCore import QDate
    self.start.setDate(QDate.currentDate());self.end.setDate(QDate.currentDate().addDays(1))
    with connect() as c:
     for rid,num,kind in c.execute("SELECT id,number,kind FROM rooms WHERE status='فعال' AND branch_id=?",(parent.active_branch,)):self.room.addItem(f'{num} - {kind}',rid)
    for title,w in [('نام مهمان',self.name),('شماره تماس',self.phone),('کد ملی (اختیاری)',self.nid),('اتاق',self.room)]:f.addRow(title,w)
    self.jalali_buttons=[]
    for title,field in [('ورود (میلادی)',self.start),('خروج (میلادی)',self.end)]:
     date_row=QHBoxLayout();date_row.addWidget(field)
     pick=QPushButton('📅 شمسی' if getattr(parent,'language','fa')=='fa' else '📅 Jalali')
     pick.setToolTip('انتخاب تاریخ از تقویم شمسی' if getattr(parent,'language','fa')=='fa' else 'Choose a date in the Jalali calendar')
     pick.clicked.connect(lambda _,edit=field:self.pick_jalali(edit))
     date_row.addWidget(pick);self.jalali_buttons.append(pick)
     f.addRow(title,date_row)
    self.validation_label=QLabel('');self.validation_label.setWordWrap(True);self.validation_label.setStyleSheet('color:#ff9b9b;font-weight:600');f.addRow(self.validation_label)
    b=QPushButton('ثبت رزرو');b.setObjectName('primary');b.clicked.connect(self.save);f.addRow(b)
    if parent is not None and getattr(parent,'language','fa')=='en':
     self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
     self.setWindowTitle('New reservation')
     for i in range(f.rowCount()):
      label=f.itemAt(i,QFormLayout.ItemRole.LabelRole)
      if label and isinstance(label.widget(),QLabel):
       widget=label.widget();widget.setText(translate(widget.text(),'en'))
     b.setText('Create reservation')
     self.name.setPlaceholderText('Full name');self.phone.setPlaceholderText('Phone number')
 def pick_jalali(self, edit):
    selected=choose_jalali_date(self,edit.date().toString('yyyy-MM-dd'),getattr(self.parent(),'language','fa'))
    if selected:
     parsed=QDate.fromString(selected,'yyyy-MM-dd')
     if parsed.isValid():edit.setDate(parsed)
 def save(self):
    name=self.name.text().strip();phone=self.phone.text().strip();start=self.start.date().toString('yyyy-MM-dd');end=self.end.date().toString('yyyy-MM-dd');rid=self.room.currentData()
    errors=validate_booking(name,phone,rid,start,end)
    self.validation_label.setText('\n'.join(translate(message, getattr(self.parent(), 'language', 'fa')) for message in errors.values()))
    for key,widget in [('name',self.name),('phone',self.phone),('room',self.room),('dates',self.start),('dates',self.end)]:
     widget.setProperty('invalid',key in errors);widget.style().unpolish(widget);widget.style().polish(widget)
    if errors:return
    try:
     with connect() as c:
      create_reservation(c,user_id=self.parent().user_id,role=self.parent().role,
       branch_id=self.parent().active_branch,room_id=rid,name=name,phone=phone,
       national_id=self.nid.text(),checkin=start,checkout=end)
     self.accept()
    except (sqlite3.Error,PermissionError,ValueError,RuntimeError) as e:
     self.validation_label.setText(translate(str(e), getattr(self.parent(), 'language', 'fa')))

def filter_table_rows(table, query):
    """Filter visible guest rows without changing database records."""
    for row in range(table.rowCount()):
        fields=[table.item(row,col).text() if table.item(row,col) else '' for col in range(table.columnCount())]
        table.setRowHidden(row,not matches_guest(fields,query))

class Main(QMainWindow):
 def __init__(self,role='admin',user_id=None,username=None):
    super().__init__();self.role=role;self.user_id=user_id;self.username=username or 'admin';set_current_actor(self.username);self.active_branch=None;self.settings=QSettings('AshkanHotelPro','HotelPMS');self.language=self.settings.value('ui/language','fa');self.language=self.language if self.language in ('fa','en') else 'fa';self.setWindowTitle('Ashkan Hotel Pro | مدیریت هتل');self.resize(1380,860);self.setMinimumSize(1050,690)
    root=QWidget()
    # Keep the shell layout LTR and mirror the sidebar explicitly per language.
    root.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    self.setCentralWidget(root)
    layout=QHBoxLayout(root);layout.setContentsMargins(16,16,16,16);layout.setSpacing(16)
    layout.setDirection(QHBoxLayout.Direction.LeftToRight)
    self.main_layout=layout
    self.stack=QStackedWidget();self.stack.setObjectName('pageStack')
    side=QFrame();side.setObjectName('side');side.setMinimumWidth(236);side.setMaximumWidth(280);side.setFixedWidth(252);self.sidebar=side
    sl=QVBoxLayout(side);sl.setContentsMargins(12,14,12,12);sl.setSpacing(8)
    brand_row=QHBoxLayout()
    logo=QSvgWidget(str(Path(__file__).with_name('assets')/'hotel_logo.svg'))
    logo.setFixedSize(42,42);brand_row.addWidget(logo)
    brand=QLabel('ASHKAN HOTEL PRO');brand.setObjectName('brandTitle');brand.setWordWrap(True)
    brand_row.addWidget(brand,1);sl.addLayout(brand_row)
    self.nav_buttons=[]
    self.nav_group_headers={}
    self.nav_search=QLineEdit()
    self.nav_search.setObjectName('navSearch')
    self.nav_search.setClearButtonEnabled(True)
    self.nav_search.setAccessibleName('Search navigation / جستجوی منو')
    self.nav_search.textChanged.connect(self.filter_navigation)
    sl.addWidget(self.nav_search)
    self.security_sidebar_button=QPushButton('🔔  اعلان‌های امنیتی' if self.language=='fa' else '🔔  Security alerts')
    self.security_sidebar_button.setObjectName('navButton')
    self.security_sidebar_button.clicked.connect(lambda:self.navigate(15))
    self.security_sidebar_button.setVisible(self.role=='admin')
    sl.addWidget(self.security_sidebar_button)
    self.security_report_button=QPushButton('📋  گزارش رویدادهای امنیتی' if self.language=='fa' else '📋  Security event report')
    self.security_report_button.setObjectName('navButton')
    self.security_report_button.clicked.connect(self.open_security_admin_report)
    self.security_report_button.setVisible(self.role=='admin')
    sl.addWidget(self.security_report_button)
    nav_scroll=QScrollArea();nav_scroll.setObjectName('navScroll');nav_scroll.setWidgetResizable(True)
    nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
    nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    nav_host=QWidget();nav_layout=QVBoxLayout(nav_host);nav_layout.setContentsMargins(0,4,0,4);nav_layout.setSpacing(6)
    nav_items=['داشبورد','اتاق‌ها','رزروها','مهمانان','پرداخت‌ها','خانه‌داری','گزارش‌ها','تنظیمات','هزینه‌ها','کارکنان','صورتحساب','تقویم رزرو','رستوران و خدمات','انبار','تحلیل درآمد','مدیریت کاربران','گزارش مالی پیشرفته','گزارش اشغال','گزارش رویدادها','تخفیف‌ها','نقشه اشغال اتاق‌ها','نرخ‌های فصلی','اعلان‌های پذیرش','مدیریت شعب','گزارش شعب','دسترسی کاربران به شعب']
    from navigation_groups import NAV_GROUPS, group_for_index, group_title
    self.nav_groups=NAV_GROUPS
    for i,title in enumerate(nav_items):
     group=group_for_index(i)
     if group not in self.nav_group_headers:
      header=QLabel(group_title(group,self.language))
      header.setObjectName('navGroupHeader')
      header.setWordWrap(True)
      nav_layout.addWidget(header)
      self.nav_group_headers[group]=header
     b=QPushButton('◈  '+title);b.setObjectName('navButton');b.setMinimumHeight(38);b.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
     b.clicked.connect(lambda _,idx=i:self.navigate(idx));nav_layout.addWidget(b);self.nav_buttons.append(b)
    nav_layout.addStretch(1)
    nav_scroll.setWidget(nav_host);sl.addWidget(nav_scroll,1)
    self.version_label=QLabel('ASHKAN HOTEL PRO  •  v119.0');self.version_label.setObjectName('versionLabel');self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter);sl.addWidget(self.version_label)
    layout.addWidget(self.stack,1);layout.addWidget(side)
    for _ in range(26):self.stack.addWidget(QWidget())
    self.statusBar().showMessage('آماده | اطلاعات در پایگاه داده محلی SQLite ذخیره می‌شود')
    self.setAccessibleName('پنجره اصلی مدیریت هتل')
    with connect() as c:
     permitted=allowed_branches(c,self.user_id,self.role) if self.user_id is not None else []
     self.active_branch=permitted[0][0] if permitted else None
    self.branch_picker=QComboBox();self.branch_picker.addItem('انتخاب شعبه',None)
    for bid,name in permitted:self.branch_picker.addItem(name,bid)
    if permitted:self.branch_picker.setCurrentIndex(1)
    self.branch_picker.currentIndexChanged.connect(self.change_branch)
    sl.insertWidget(1,self.branch_picker)
    self.language_picker=QComboBox()
    self.language_picker.addItem('فارسی', 'fa')
    self.language_picker.addItem('English', 'en')
    self.language_picker.setAccessibleName('Language / زبان')
    sl.insertWidget(1,self.language_picker)
    self.language_picker.setCurrentIndex(1 if self.language=='en' else 0)
    self.language_picker.currentIndexChanged.connect(self.change_language)
    self.branch_picker.setAccessibleName('انتخاب شعبه فعال')
    self.branch_picker.setToolTip('انتخاب شعبه‌ای که داده‌های مجاز آن نمایش داده می‌شود')
    for button in self.nav_buttons:button.setMinimumHeight(38)
    self.apply_language_direction()
    self.refresh_language()
    self.navigate(0)
    self._security_monitor_retry_attempt=0
    self._security_monitor_state="idle"
    self.security_monitor_timer=QTimer(self)
    self.security_monitor_retry_timer=QTimer(self)
    self.security_monitor_retry_timer.setSingleShot(True)
    self.security_monitor_retry_timer.timeout.connect(self.poll_security_monitor)
    self.security_monitor_timer.timeout.connect(self.poll_security_monitor)
 def open_security_admin_report(self):
    """Open the security-event report after revalidating the current session and permission."""
    if self.user_id is None or not getattr(self,'session_token',None):
     QMessageBox.warning(self,'عدم دسترسی' if self.language=='fa' else 'Access denied',
       'نشست معتبر نیست؛ دوباره وارد شوید.' if self.language=='fa' else 'No active session. Please sign in again.')
     return
    try:
     from operation_guard import authorize_action
     from security_admin_panel_v166 import SecurityAdminPanel
     with connect() as db:
      authorize_action(db,self.user_id,self.session_token,'security.view')
      dialog=SecurityAdminPanel(db,self.language,self)
      dialog.exec()
    except (PermissionError,ValueError,sqlite3.Error,RuntimeError) as exc:
     QMessageBox.warning(self,'عدم دسترسی' if self.language=='fa' else 'Access denied',str(exc))
 def start_security_monitor(self):
    """Configure timer; database work on each tick runs in a separate thread."""
    if self.role!='admin' or self.user_id is None or not getattr(self,'session_token',None):return
    try:
     from security_monitor_v116 import get_settings
     from operation_guard import authorize_action
     with connect() as db:
      authorize_action(db,self.user_id,self.session_token,'security.view')
      config=get_settings(db,self.user_id)
     if config['enabled']:
      self._security_monitor_state="scheduled"
      self.security_monitor_timer.start(config['interval_seconds']*1000)
     else:
      self.security_monitor_timer.stop()
      self.security_monitor_retry_timer.stop()
      self._security_monitor_state="disabled"
    except (PermissionError,ValueError,sqlite3.Error,AttributeError):
     self.security_monitor_timer.stop()
 def poll_security_monitor(self):
    """Launch a single worker without blocking the UI or overlapping polls."""
    if not getattr(self,'session_token',None) or self.role!='admin':return
    if getattr(self,'_security_monitor_worker',None) is not None:return
    from security_monitor_worker_v117 import SecurityMonitorWorker
    if SecurityMonitorWorker is None:
     self.security_monitor_timer.stop()
     return
    self._security_monitor_state="running"
    worker=SecurityMonitorWorker(DB,self.user_id,self.session_token,self)
    self._security_monitor_worker=worker
    worker.succeeded.connect(self._security_monitor_success)
    worker.failed.connect(self._security_monitor_failure)
    worker.finished.connect(self._security_monitor_finished)
    worker.start()
 def _security_monitor_success(self,result):
    self._security_monitor_retry_attempt=0
    self.security_monitor_retry_timer.stop()
    self._security_monitor_last_error=None
    self._security_monitor_state="healthy"
    if result.get('enabled'):
     count=result.get('unread',0)
     self.security_sidebar_button.setText(('🔔  هشدارهای امنیتی' if self.language=='fa' else '🔔  Security alerts')+f' ({count})')
     self.security_sidebar_button.setVisible(True)
    else:self.security_monitor_timer.stop()
 def _security_monitor_failure(self,message):
    """Fail closed, avoid intrusive message boxes on periodic checks."""
    from security_monitor_status_v118 import classify_error,retry_delay_seconds
    self._security_monitor_last_error=message
    category=classify_error(message)
    if category=='authorization':
     self.security_monitor_timer.stop()
     self.security_monitor_retry_timer.stop()
     self._security_monitor_state='authorization_failed'
    elif self._security_monitor_retry_attempt < 3:
     self._security_monitor_retry_attempt+=1
     self._security_monitor_state='retry_wait'
     self.security_monitor_timer.stop()
     self.security_monitor_retry_timer.start(retry_delay_seconds(self._security_monitor_retry_attempt)*1000)
    else:
     self.security_monitor_timer.stop()
     self._security_monitor_state='failed'
    try:
     from security_monitor_status_v118 import record_failure
     with connect() as db:record_failure(db,self.user_id,message,self._security_monitor_retry_attempt)
    except (PermissionError,ValueError,sqlite3.Error):pass
 def _security_monitor_finished(self):
    worker=getattr(self,'_security_monitor_worker',None)
    if worker is not None:
     worker.deleteLater()
     self._security_monitor_worker=None
     if self._security_monitor_state=='healthy' and not self.security_monitor_timer.isActive():
      self.start_security_monitor()
 def closeEvent(self,event):
    """Stop scheduling; let an in-flight database operation finish safely."""
    if hasattr(self,'security_monitor_timer'):
     self.security_monitor_timer.stop()
    worker=getattr(self,'_security_monitor_worker',None)
    if worker is not None and worker.isRunning():
     worker.wait(7000)
     if worker.isRunning():
      event.ignore()
      return
    super().closeEvent(event)
 def apply_language_direction(self):
    """Apply a true application-wide RTL/LTR layout and mirror the shell navigation."""
    direction=Qt.LayoutDirection.RightToLeft if self.language=='fa' else Qt.LayoutDirection.LeftToRight
    app=QApplication.instance()
    if app is not None:
     app.setLayoutDirection(direction)
    self.setLayoutDirection(direction)
    # Root shell remains LTR; explicitly order the sidebar to avoid double mirroring.
    self.centralWidget().setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    self.main_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
    self.main_layout.removeWidget(self.sidebar)
    self.main_layout.removeWidget(self.stack)
    if self.language == 'fa':
     self.main_layout.addWidget(self.stack, 1)
     self.main_layout.addWidget(self.sidebar)
    else:
     self.main_layout.addWidget(self.sidebar)
     self.main_layout.addWidget(self.stack, 1)
    self.sidebar.setLayoutDirection(direction)
    self.nav_search.setLayoutDirection(direction)
    self.stack.setLayoutDirection(direction)
    # Explicitly update all current descendants, including nested pages/dialog controls.
    for widget in self.findChildren(QWidget):
     if widget is self.centralWidget():
      continue
     widget.setLayoutDirection(direction)
    self.centralWidget().setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    self.main_layout.setDirection(QHBoxLayout.Direction.LeftToRight)
    self.setWindowTitle('Ashkan Hotel Pro  |  '+('مدیریت هتل' if self.language=='fa' else 'Hotel Management'))
    # Direction-aware alignment: avoid Persian right-aligned controls in English mode.
    align='right' if self.language=='fa' else 'left'
    self.setStyleSheet(STYLE + f'\nQPushButton {{ text-align: {align}; }}\nQLabel#subtitle {{ text-align: {align}; }}')
 def change_language(self,_):
    language=self.language_picker.currentData()
    if language not in ('fa','en') or language==self.language:return
    self.language=language
    self.settings.setValue('ui/language',language)
    self.apply_language_direction()
    self.refresh_language()
    self.navigate(self.stack.currentIndex())
 def refresh_language(self):
    self.security_sidebar_button.setText('🔔  اعلان‌های امنیتی' if self.language=='fa' else '🔔  Security alerts')
    self.security_report_button.setText('📋  گزارش رویدادهای امنیتی' if self.language=='fa' else '📋  Security event report')
    # Navigation labels are regenerated from canonical Persian identifiers.
    for index,button in enumerate(self.nav_buttons):
     button.setText('◈  '+(NAV_FA[index] if self.language=='fa' else NAV_EN[index]))
    from navigation_groups import group_title
    for group,header in self.nav_group_headers.items():
     header.setText(group_title(group,self.language))
    self.branch_picker.setItemText(0, 'انتخاب شعبه' if self.language=='fa' else 'Select branch')
    self.nav_search.setPlaceholderText('جستجوی بخش‌ها…' if self.language=='fa' else 'Search sections…')
    self.filter_navigation(self.nav_search.text())
    self._translate_page(self.stack.currentWidget())
 def filter_navigation(self, query):
    # Search against both languages, so switching language does not hide a match.
    visible=matching_navigation_indices(query,NAV_FA,NAV_EN)
    for index,button in enumerate(self.nav_buttons):
     button.setVisible(index in visible)
    from navigation_groups import group_for_index, visible_groups
    groups=visible_groups(visible)
    for group,header in self.nav_group_headers.items():
     header.setVisible(group in groups)
 def _translate_page(self,widget):
    if widget is None:return
    # Reversible translation: always render from the original Persian UI text.
    # Do not modify table body cells, stored statuses or payment method values.
    for child in [widget]+widget.findChildren(QWidget):
     if isinstance(child,(QLabel,QPushButton)):
      original=child.property('source_fa_text')
      if original is None:
       original=child.text();child.setProperty('source_fa_text',original)
      child.setText(translate(original,self.language))
     elif isinstance(child,QLineEdit):
      original=child.property('source_fa_placeholder')
      if original is None:
       original=child.placeholderText();child.setProperty('source_fa_placeholder',original)
      child.setPlaceholderText(translate(original,self.language))
     elif isinstance(child,QComboBox):
      for j in range(child.count()):
       original=child.itemData(j,Qt.ItemDataRole.UserRole+1)
       if original is None:
        original=child.itemText(j);child.setItemData(j,original,Qt.ItemDataRole.UserRole+1)
       child.setItemText(j,translate(original,self.language))
     elif isinstance(child,QTableWidget):
      for j in range(child.columnCount()):
       item=child.horizontalHeaderItem(j)
       if item:
        original=item.data(Qt.ItemDataRole.UserRole)
        if original is None:
         original=item.text();item.setData(Qt.ItemDataRole.UserRole,original)
        item.setText(translate(original,self.language))
 def change_branch(self,_):
    branch=self.branch_picker.currentData()
    if branch is None:return
    with connect() as c:require_branch(c,self.user_id,self.role,branch)
    self.active_branch=branch
    self.statusBar().showMessage(('Active branch: ' if self.language=='en' else 'شعبه فعال: ')+self.branch_picker.currentText())
    self.navigate(0)
 def format_date(self,value):
    return display_date(value,self.language)
 def format_money(self,value):
    return display_money(value,self.language)
 def page(self,title):
    w=QWidget();v=QVBoxLayout(w)
    v.setContentsMargins(12,12,12,16);v.setSpacing(16)
    h=QLabel(title);h.setObjectName('title');h.setWordWrap(True)
    v.addWidget(h)
    return w,v
 def table(self,headers,rows):
    t=QTableWidget(len(rows),len(headers));t.setMinimumHeight(320);t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows);t.setHorizontalHeaderLabels(headers);t.setAlternatingRowColors(True);t.setSortingEnabled(False);t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    for i,row in enumerate(rows):
     for j,val in enumerate(row):t.setItem(i,j,QTableWidgetItem(str(val)))
    t.verticalHeader().setVisible(False);t.setShowGrid(False);t.setWordWrap(False)
    t.setSortingEnabled(True)
    t.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    t.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    t.customContextMenuRequested.connect(lambda point, table=t: self.show_table_menu(table, point))
    shortcut=QShortcut(QKeySequence.StandardKey.Copy,t)
    shortcut.activated.connect(lambda table=t:self.copy_table_selection(table))
    t._copy_shortcut=shortcut
    search_shortcut=QShortcut(QKeySequence('Ctrl+F'),t)
    search_shortcut.activated.connect(lambda table=t:self.prompt_table_filter(table))
    t._search_shortcut=search_shortcut
    # Live search is attached to the table as a self-contained toolbar.
    # Existing pages continue to add the returned QTableWidget as before.
    t._live_search=QLineEdit(t)
    t._live_search.setPlaceholderText('جست‌وجوی زنده در تمام ستون‌ها…')
    t._live_search.setClearButtonEnabled(True)
    t._live_search.setAccessibleName('جست‌وجوی زنده در جدول')
    t._live_search.textChanged.connect(lambda query, table=t:self.apply_table_filter(table,query))
    t._live_search.setVisible(False)
    t._live_search.setStyleSheet('QLineEdit {background:#132a40;border:2px solid #13b8aa;border-radius:10px;padding:8px;color:white;}')
    t._search_shortcut.activated.disconnect()
    t._search_shortcut.activated.connect(lambda table=t:self.toggle_live_search(table))
    t.setToolTip('برای جست‌وجوی زنده Ctrl+F یا راست‌کلیک کنید')
    t.setAccessibleName('جدول اطلاعات؛ برای کپی Ctrl+C را بزنید')
    return t
 def toggle_live_search(self,table):
    field=table._live_search
    if field.isVisible():
     field.clear();field.hide();table.setFocus()
    else:
     field.setGeometry(12,8,max(180,table.width()-40),40)
     field.show();field.raise_();field.setFocus()
 def copy_table_selection(self, table):
    indexes=table.selectedIndexes()
    if not indexes:return
    rows=sorted({i.row() for i in indexes if not table.isRowHidden(i.row())})
    columns=sorted({i.column() for i in indexes})
    lines=[]
    for row in rows:
     fields=[]
     for col in columns:
      cell=table.item(row,col)
      fields.append(cell.text().replace('\t',' ').replace('\n',' ') if cell and cell.isSelected() else '')
     lines.append('\t'.join(fields))
    QApplication.clipboard().setText('\n'.join(lines))
    self.statusBar().showMessage(f'{len(rows)} ردیف در کلیپ‌بورد کپی شد',4000)
 def show_table_menu(self,table,point):
    menu=QMenu(table)
    action=menu.addAction('کپی سلول‌های انتخاب‌شده (Ctrl+C)')
    action.setEnabled(bool(table.selectedIndexes()))
    menu.addSeparator()
    search_action=menu.addAction('جست‌وجو / فیلتر جدول (Ctrl+F)')
    clear_action=menu.addAction('حذف فیلتر جدول')
    selected=menu.exec(table.viewport().mapToGlobal(point))
    if selected==action:self.copy_table_selection(table)
    elif selected==search_action:self.prompt_table_filter(table)
    elif selected==clear_action:
     table._live_search.clear();self.apply_table_filter(table,'')
 def apply_table_filter(self,table,query):
    shown=0
    for row in range(table.rowCount()):
     values=[table.item(row,col).text() if table.item(row,col) else '' for col in range(table.columnCount())]
     matched=row_matches(values,query)
     table.setRowHidden(row,not matched)
     shown+=int(matched)
    table._filter_query=query
    self.statusBar().showMessage(f'نمایش {shown} از {table.rowCount()} ردیف',5000)
 def prompt_table_filter(self,table):
    query,ok=QInputDialog.getText(self,'جست‌وجو در جدول','عبارت جست‌وجو (چند کلمه مجاز است):',text=getattr(table,'_filter_query',''))
    if ok:
     self.apply_table_filter(table,query)
     table._live_search.setText(query)

 def ensure_admin(self):
    from security_overview import require_permission
    try:
     with connect() as db:require_permission(db,self.user_id,'users.manage')
    except (PermissionError,ValueError,sqlite3.Error):
     QMessageBox.warning(self,'عدم دسترسی','این بخش تنها برای مدیر فعال مجاز است.');return False
    if self.role!='admin':
     QMessageBox.warning(self,'عدم دسترسی','این بخش تنها برای مدیر مجاز است.');return False
    return True
 def authorize_operation(self, action):
    from operation_guard import authorize_action
    try:
     with connect() as db:
      authorize_action(db,self.user_id,getattr(self,'session_token',None),action)
     return True
    except (PermissionError,ValueError,sqlite3.Error) as exc:
     QMessageBox.warning(self,'عدم دسترسی' if self.language=='fa' else 'Access denied',str(exc))
     return False
 def create_user(self):
    if not self.authorize_operation('users.create'):return
    if not self.ensure_admin():return
    username,ok=QInputDialog.getText(self,'کاربر جدید','نام کاربری:')
    if not ok or not username.strip():return
    password,ok=QInputDialog.getText(self,'کاربر جدید','رمز عبور (حداقل ۱۲ نویسه):',QLineEdit.EchoMode.Password)
    if not ok:return
    from first_run_security import validate_admin_credentials
    try:validate_admin_credentials(username,password,password)
    except ValueError as exc:QMessageBox.warning(self,'خطا',str(exc));return
    role,ok=QInputDialog.getItem(self,'نقش کاربر','نقش:', ['reception','admin'],0,False)
    if not ok:return
    salt=secrets.token_hex(16);digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),240000).hex()
    try:
     with connect() as c:
      c.execute('INSERT INTO users(username,password_hash,salt,role) VALUES(?,?,?,?)',(username.strip(),digest,salt,role))
      target=c.execute('SELECT id FROM users WHERE username=?',(username.strip(),)).fetchone()[0]
      c.execute('INSERT INTO security_events(actor_id,target_id,event) VALUES(?,?,?)',(self.user_id,target,'account_created'))
     audit(self.username,'create_user',username.strip()+' / '+role);self.navigate(15)
    except sqlite3.IntegrityError:QMessageBox.warning(self,'خطا','این نام کاربری تکراری است.')
 def financial_export(self):
    if not self.authorize_operation('finance.export'):return
    if not self.ensure_admin():return
    path,_=QFileDialog.getSaveFileName(self,'گزارش مالی','hotel-finance.csv','CSV (*.csv)')
    if not path:return
    try:
     with connect() as c:
      require_branch(c,self.user_id,self.role,self.active_branch)
      payments=c.execute('''SELECT p.created_at,p.amount,p.method FROM payments p
       JOIN reservations r ON r.id=p.reservation_id
       JOIN rooms ro ON ro.id=r.room_id
       WHERE COALESCE(r.branch_id,ro.branch_id)=? ORDER BY p.created_at''',(self.active_branch,)).fetchall()
      expenses=[]  # Expenses are not yet assigned to a branch; do not mix them into a branch export.
     with open(path,'w',newline='',encoding='utf-8-sig') as f:
      writer=csv.writer(f);writer.writerow(['تاریخ','نوع','شرح','مبلغ (تومان)'])
      writer.writerows((d,'دریافت',m,a) for d,a,m in payments)
      writer.writerows((d,'هزینه',cat,-a) for d,a,cat in expenses)
     QMessageBox.information(self,'گزارش','دریافتی‌های شعبه فعال ذخیره شد. هزینه‌های فاقد شعبه در این گزارش نیستند.')
    except (OSError,sqlite3.Error) as e:QMessageBox.critical(self,'خطا',str(e))
 def export_invoice_pdf(self):
    if not self.authorize_operation('reservations.invoice'):return
    rid=self.invoice_res.currentData()
    if rid is None:return
    language=self.language if self.language in ('fa','en') else 'fa'
    title='ذخیره صورتحساب' if language=='fa' else 'Save invoice'
    path,_=QFileDialog.getSaveFileName(self,title,f'invoice-{rid}.pdf','PDF (*.pdf)')
    if not path:return
    try:
     with connect() as c:
      authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
      inv=calculate_invoice(c,rid)
     write_invoice_pdf(path,inv,language,self.format_date,self.format_money)
     QMessageBox.information(self,'موفق' if language=='fa' else 'Success','صورتحساب PDF ذخیره شد.' if language=='fa' else 'Invoice PDF saved successfully.')
    except Exception as e:
     QMessageBox.critical(self,'خطای PDF' if language=='fa' else 'PDF error',str(e))
 def open_booking_audit(self):
    if self.role!='admin':
     QMessageBox.warning(self,'عدم دسترسی' if self.language=='fa' else 'Access denied','فقط مدیر سامانه به تاریخچه کامل دسترسی دارد.' if self.language=='fa' else 'Only system administrators can access the full audit timeline.')
     return
    dialog=BookingAuditDialog(connect,self.language,self)
    dialog.exec()
 def navigate(self,i):
    from security_sessions import validate_session,touch_session
    if getattr(self,'session_token',None):
     with connect() as db:
      if not validate_session(db,self.session_token):
       QMessageBox.warning(self,'Session expired','Please sign in again.')
       self.close()
       return
      touch_session(db,self.session_token)
    from security_overview import require_permission
    try:
     with connect() as db:
      permission='users.manage' if i==15 else ('finance.manage' if i in (8,9,13,14,16,18,19,21) else ('branches.manage' if i in (23,24,25) else 'reservations.view'))
      require_permission(db,self.user_id,permission)
      current_role=db.execute('SELECT role FROM users WHERE id=?',(self.user_id,)).fetchone()
      if current_role:self.role=current_role[0]
    except (PermissionError,ValueError,sqlite3.Error):
     QMessageBox.warning(self,'عدم دسترسی' if self.language=='fa' else 'Access denied',
       'مجوز دسترسی معتبر نیست.' if self.language=='fa' else 'Permission denied or account disabled.')
     return
    with connect() as c:
     if i==25:
      w,v=self.page('مدیریت دسترسی کاربران به شعب')
      user=QComboBox();branch=QComboBox()
      for uid,uname in c.execute('SELECT id,username FROM users ORDER BY username'):user.addItem(uname,uid)
      for bid,bname in allowed_branches(c,self.user_id,self.role):branch.addItem(bname,bid)
      v.addWidget(QLabel('کاربر'));v.addWidget(user);v.addWidget(QLabel('شعبه'));v.addWidget(branch)
      listing=QTableWidget();v.addWidget(listing)
      def refresh_access():
       with connect() as db:
        rows=db.execute('SELECT u.username,b.name FROM user_branches ub JOIN users u ON u.id=ub.user_id JOIN branches b ON b.id=ub.branch_id ORDER BY u.username,b.name').fetchall()
       listing.setColumnCount(2);listing.setRowCount(len(rows));listing.setHorizontalHeaderLabels(['کاربر','شعبه'])
       for ri,record in enumerate(rows):
        for ci,value in enumerate(record):listing.setItem(ri,ci,QTableWidgetItem(str(value)))
      def apply_access(revoke=False):
       try:
        with connect() as db:
         operation=revoke_user_branch if revoke else grant_user_branch
         operation(db,self.user_id,self.role,user.currentData(),branch.currentData())
        audit(self.username,'branch_access_revoked' if revoke else 'branch_access_granted',f'{user.currentData()} / {branch.currentData()}')
        refresh_access()
       except (PermissionError,ValueError,sqlite3.Error) as exc:QMessageBox.warning(self,'دسترسی',str(exc))
      grant=QPushButton('اعطای دسترسی');grant.setObjectName('primary');grant.clicked.connect(lambda:apply_access(False));v.addWidget(grant)
      revoke=QPushButton('لغو دسترسی');revoke.clicked.connect(lambda:apply_access(True));v.addWidget(revoke);refresh_access()
     elif i==24:
      w,v=self.page('داشبورد تحلیلی شعب')
      v.addWidget(QLabel('گزارش مستقل هر شعبه بر اساس اتاق و رزرو؛ دریافتی فقط پرداخت‌های ثبت‌شده است.'))
      controls=QHBoxLayout();branch_filter=QComboBox();controls.addWidget(branch_filter)
      start=QDateEdit();start.setCalendarPopup(True);start.setDate(QDate.currentDate().addDays(-30));controls.addWidget(start)
      end=QDateEdit();end.setCalendarPopup(True);end.setDate(QDate.currentDate());controls.addWidget(end)
      # Jalali calendar selection uses ISO Gregorian dates internally for SQLite.
      def select_jalali_for(widget):
       picked=choose_jalali_date(self,widget.date().toString('yyyy-MM-dd'),self.language)
       if picked:
        widget.setDate(QDate.fromString(picked,'yyyy-MM-dd'))
      if self.language=='fa':
       start_jalali=QPushButton('📅 شروع شمسی')
       end_jalali=QPushButton('📅 پایان شمسی')
       start_jalali.clicked.connect(lambda:select_jalali_for(start))
       end_jalali.clicked.connect(lambda:select_jalali_for(end))
       controls.addWidget(start_jalali);controls.addWidget(end_jalali)
      # Persist report preferences per user, without storing any financial data.
      report_key=f'reports/branch/{self.user_id or "admin"}'
      saved_start=self.settings.value(report_key+'/start',None)
      saved_end=self.settings.value(report_key+'/end',None)
      for widget,saved in ((start,saved_start),(end,saved_end)):
       if saved:
        parsed=QDate.fromString(str(saved),'yyyy-MM-dd')
        if parsed.isValid():widget.setDate(parsed)
      sort_selector=QComboBox()
      for label,key in ([('دریافتی','receipts'),('هزینه','expenses'),('خالص','net'),('نام شعبه','branch')] if self.language=='fa' else [('Receipts','receipts'),('Expenses','expenses'),('Net','net'),('Branch name','branch')]):
       sort_selector.addItem(label,key)
      saved_sort=str(self.settings.value(report_key+'/sort','receipts'))
      saved_sort_index=sort_selector.findData(saved_sort)
      if saved_sort_index>=0:sort_selector.setCurrentIndex(saved_sort_index)
      controls.addWidget(sort_selector)
      sort_direction=QComboBox()
      sort_direction.addItem('نزولی' if self.language=='fa' else 'Descending',True)
      sort_direction.addItem('صعودی' if self.language=='fa' else 'Ascending',False)
      if str(self.settings.value(report_key+'/descending','true')).lower()=='false':sort_direction.setCurrentIndex(1)
      controls.addWidget(sort_direction)
      refresh=QPushButton('نمایش گزارش');refresh.setObjectName('primary');controls.addWidget(refresh);v.addLayout(controls)
      metrics=QLabel();metrics.setObjectName('metric');v.addWidget(metrics)
      reservations_table=QTableWidget();v.addWidget(reservations_table)
      for bid,name in allowed_branches(c,self.user_id,self.role):
       branch_filter.addItem(name,bid)
      saved_branch=self.settings.value(report_key+'/branch',None)
      if saved_branch is not None:
       try:saved_index=branch_filter.findData(int(saved_branch))
       except (ValueError,TypeError):saved_index=-1
       if saved_index>=0:branch_filter.setCurrentIndex(saved_index)
      def save_report_preferences():
       self.settings.setValue(report_key+'/start',start.date().toString('yyyy-MM-dd'))
       self.settings.setValue(report_key+'/end',end.date().toString('yyyy-MM-dd'))
       if branch_filter.currentData() is not None:self.settings.setValue(report_key+'/branch',branch_filter.currentData())
       self.settings.setValue(report_key+'/sort',sort_selector.currentData())
       self.settings.setValue(report_key+'/descending','true' if sort_direction.currentData() else 'false')
      branch_filter.currentIndexChanged.connect(lambda _:save_report_preferences())
      start.dateChanged.connect(lambda _:save_report_preferences())
      end.dateChanged.connect(lambda _:save_report_preferences())
      sort_selector.currentIndexChanged.connect(lambda _:save_report_preferences())
      sort_direction.currentIndexChanged.connect(lambda _:save_report_preferences())
      def load_branch_report():
       try:
        with connect() as db:
         bid=branch_filter.currentData()
         require_branch(db,self.user_id,self.role,bid)
         summary=branch_summary(db,bid,start.date().toString('yyyy-MM-dd'),end.date().addDays(1).toString('yyyy-MM-dd'))
         rows=branch_reservations(db,bid,start.date().toString('yyyy-MM-dd'),end.date().addDays(1).toString('yyyy-MM-dd'))
        metrics.setText(f"اتاق‌ها: {summary['rooms']}    |    رزروها: {summary['reservations']}    |    شب‌اتاق اشغال: {summary['occupied_nights']}    |    دریافتی: {self.format_money(summary['payments'])}")
        reservations_table.setColumnCount(5);reservations_table.setRowCount(len(rows))
        reservations_table.setHorizontalHeaderLabels(['رزرو','اتاق','مهمان','ورود','خروج'])
        for ri,record in enumerate(rows):
         for ci,value in enumerate(record):reservations_table.setItem(ri,ci,QTableWidgetItem(str(value)))
        reservations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       except (ValueError,sqlite3.Error) as exc:QMessageBox.warning(self,'خطا',str(exc))
      refresh.clicked.connect(load_branch_report)
      export_button=QPushButton('خروجی Excel / CSV' if self.language=='fa' else 'Export Excel / CSV')
      export_button.setObjectName('primary')
      controls.addWidget(export_button)
      def export_branch_report():
       bid=branch_filter.currentData()
       if bid is None:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error','شعبه‌ای انتخاب نشده است.' if self.language=='fa' else 'Select a branch first.');return
       first=start.date().toString('yyyy-MM-dd')
       last=end.date().addDays(1).toString('yyyy-MM-dd')
       if first>=last:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error','بازه تاریخ نامعتبر است.' if self.language=='fa' else 'Invalid date range.');return
       filename,selected_filter=QFileDialog.getSaveFileName(self,'ذخیره گزارش شعبه' if self.language=='fa' else 'Save branch report',f'branch_{bid}_reservations.xlsx','Excel Workbook (*.xlsx);;CSV (*.csv)')
       if not filename:return
       try:
        with connect() as db:
         require_branch(db,self.user_id,self.role,bid)
         records=branch_reservations(db,bid,first,last)
        if selected_filter.startswith('CSV'):
         filename=filename if filename.lower().endswith('.csv') else filename+'.csv'
         export_branch_reservations(filename,records,self.language)
        else:
         filename=filename if filename.lower().endswith('.xlsx') else filename+'.xlsx'
         export_branch_workbook(filename,records,self.language,branch_filter.currentText(),first,end.date().toString('yyyy-MM-dd'))
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      export_button.clicked.connect(export_branch_report)
      executive_button=QPushButton('گزارش مدیریتی Excel' if self.language=='fa' else 'Executive Excel Report')
      executive_button.setObjectName('primary')
      controls.addWidget(executive_button)
      def export_executive_report():
       bid=branch_filter.currentData()
       if bid is None:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error','شعبه‌ای انتخاب نشده است.' if self.language=='fa' else 'Select a branch first.');return
       first=start.date().toString('yyyy-MM-dd')
       last=end.date().addDays(1).toString('yyyy-MM-dd')
       if first>=last:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error','بازه تاریخ نامعتبر است.' if self.language=='fa' else 'Invalid date range.');return
       filename,_=QFileDialog.getSaveFileName(self,'گزارش مدیریتی Excel' if self.language=='fa' else 'Executive Excel Report',f'branch_{bid}_management.xlsx','Excel Workbook (*.xlsx)')
       if not filename:return
       try:
        with connect() as db:
         require_branch(db,self.user_id,self.role,bid)
         report=branch_summary(db,bid,first,last)
         bookings=branch_reservations(db,bid,first,last)
         # Authorization and branch scope are enforced by scoped_payments.
         branch_payments=scoped_payments(db,self.user_id,self.role,bid)
         filtered=[p for p in branch_payments if first<=str(p[4])[:10]<last]
        filename=filename if filename.lower().endswith('.xlsx') else filename+'.xlsx'
        export_management_workbook(filename,branch_name=branch_filter.currentText(),start=first,end=last,summary=report,reservations=bookings,payments=filtered,language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,KeyError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      executive_button.clicked.connect(export_executive_report)

      comparison_button=QPushButton('مقایسه شعب Excel' if self.language=='fa' else 'Compare Branches Excel')
      comparison_button.setObjectName('primary');controls.addWidget(comparison_button)
      def export_branch_comparison():
       first=start.date().toString('yyyy-MM-dd')
       last=end.date().addDays(1).toString('yyyy-MM-dd')
       filename,_=QFileDialog.getSaveFileName(self,'مقایسه شعب' if self.language=='fa' else 'Branch comparison','branch_comparison.xlsx','Excel Workbook (*.xlsx)')
       if not filename:return
       try:
        with connect() as db:
         report=authorized_comparison(db,user_id=self.user_id,role=self.role,start=first,end=last)
        filename=filename if filename.lower().endswith('.xlsx') else filename+'.xlsx'
        export_comparison_workbook(filename,report,start=first,end=last,language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,KeyError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      comparison_button.clicked.connect(export_branch_comparison)
      performance_button=QPushButton('شاخص‌های تخمینی اقامت Excel' if self.language=='fa' else 'Indicative Stay KPIs Excel')
      controls.addWidget(performance_button)
      def export_stay_performance():
       first=start.date().toString('yyyy-MM-dd')
       last=end.date().addDays(1).toString('yyyy-MM-dd')
       filename,_=QFileDialog.getSaveFileName(self,'شاخص‌های اقامت' if self.language=='fa' else 'Stay KPIs','stay_kpis.xlsx','Excel Workbook (*.xlsx)')
       if not filename:return
       try:
        with connect() as db:
         branches=allowed_branches(db,self.user_id,self.role)
         report=[]
         for bid,name in branches:
          record=estimated_branch_performance(db,branch_id=bid,start=first,end=last,user_id=self.user_id,role=self.role)
          report.append(dict(branch_name=name,**record))
        filename=filename if filename.lower().endswith('.xlsx') else filename+'.xlsx'
        export_estimated_performance(filename,report,start=first,end=last,language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش تخمینی ذخیره شد.' if self.language=='fa' else 'Indicative report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,KeyError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      performance_button.clicked.connect(export_stay_performance)

      # Live, branch-scoped cash movement cards (receipts less allocated expenses).
      cash_cards=QLabel();cash_cards.setWordWrap(True);cash_cards.setObjectName('metric');v.addWidget(cash_cards)
      branch_search=QLineEdit()
      branch_search.setPlaceholderText('جست‌وجوی نام شعبه...' if self.language=='fa' else 'Search branch name...')
      branch_search.setClearButtonEnabled(True)
      branch_search.setToolTip('فقط نتایج مجاز را فیلتر می‌کند' if self.language=='fa' else 'Filters authorized results only')
      v.addWidget(branch_search)
      advanced_controls=QHBoxLayout();v.addLayout(advanced_controls)
      metric_filter=QComboBox()
      for label,key in ((('خالص' if self.language=='fa' else 'Net'),'net'),(('دریافتی' if self.language=='fa' else 'Receipts'),'receipts'),(('هزینه' if self.language=='fa' else 'Expenses'),'expenses')):
       metric_filter.addItem(label,key)
      advanced_controls.addWidget(metric_filter)
      minimum_filter=QLineEdit();minimum_filter.setPlaceholderText('حداقل مبلغ' if self.language=='fa' else 'Minimum amount');advanced_controls.addWidget(minimum_filter)
      maximum_filter=QLineEdit();maximum_filter.setPlaceholderText('حداکثر مبلغ' if self.language=='fa' else 'Maximum amount');advanced_controls.addWidget(maximum_filter)
      state_filter=QComboBox()
      for label,key in ((('همه' if self.language=='fa' else 'All'),'all'),(('مثبت' if self.language=='fa' else 'Positive'),'positive'),(('منفی' if self.language=='fa' else 'Negative'),'negative'),(('صفر' if self.language=='fa' else 'Zero'),'zero')):
       state_filter.addItem(label,key)
      advanced_controls.addWidget(state_filter)
      # Per-user, per-role filter settings. Restored only to validated controls.
      for widget, key in ((branch_search,'search'),(minimum_filter,'minimum'),(maximum_filter,'maximum')):
       widget.setText(str(self.settings.value(report_key+'/'+key,'')))
      for widget,key,default in ((metric_filter,'metric','net'),(state_filter,'state','all')):
       index=widget.findData(str(self.settings.value(report_key+'/'+key,default)))
       if index>=0:widget.setCurrentIndex(index)
      def save_advanced_preferences():
       for widget,key in ((branch_search,'search'),(minimum_filter,'minimum'),(maximum_filter,'maximum')):
        self.settings.setValue(report_key+'/'+key,widget.text())
       self.settings.setValue(report_key+'/metric',metric_filter.currentData())
       self.settings.setValue(report_key+'/state',state_filter.currentData())
      branch_search.textChanged.connect(lambda _:save_advanced_preferences())
      minimum_filter.editingFinished.connect(save_advanced_preferences)
      maximum_filter.editingFinished.connect(save_advanced_preferences)
      metric_filter.currentIndexChanged.connect(lambda _:save_advanced_preferences())
      state_filter.currentIndexChanged.connect(lambda _:save_advanced_preferences())
      reset_filters=QPushButton('پاک‌کردن فیلترهای مالی' if self.language=='fa' else 'Clear Financial Filters')
      v.addWidget(reset_filters)
      def clear_financial_filters():
       branch_search.clear();minimum_filter.clear();maximum_filter.clear()
       metric_filter.setCurrentIndex(0);state_filter.setCurrentIndex(0)
       save_advanced_preferences();load_cash_comparison()
      reset_filters.clicked.connect(clear_financial_filters)
      visible_summary=QLabel()
      visible_summary.setObjectName('metric');visible_summary.setWordWrap(True)
      v.addWidget(visible_summary)
      # Executive KPIs always derive from the same permission-scoped visible rows.
      executive_kpi_title=QLabel('نمای مدیریتی شعب فیلترشده' if self.language=='fa' else 'Filtered Branch Executive Overview')
      executive_kpi_title.setObjectName('title');v.addWidget(executive_kpi_title)
      executive_kpi_panel=QFrame();executive_kpi_panel.setObjectName('executiveKpis')
      executive_kpi_panel.setStyleSheet('QFrame#executiveKpis{background:#172b40;border:1px solid #35526a;border-radius:12px;} QLabel{color:#e9f3f9;}')
      executive_kpi_layout=QGridLayout(executive_kpi_panel)
      executive_kpi_widgets=[]
      for _ in range(5):
       tile=QFrame();tile.setStyleSheet('QFrame{background:#223d54;border-radius:8px;padding:6px;}')
       tile_layout=QVBoxLayout(tile)
       label=QLabel();label.setWordWrap(True);label.setStyleSheet('font-size:11px;color:#b9d1e0;')
       value=QLabel();value.setWordWrap(True);value.setStyleSheet('font-size:17px;font-weight:700;color:#ffffff;')
       tile_layout.addWidget(label);tile_layout.addWidget(value)
       executive_kpi_layout.addWidget(tile, len(executive_kpi_widgets)//3, len(executive_kpi_widgets)%3);executive_kpi_widgets.append((label,value))
      v.addWidget(executive_kpi_panel)
      # Compare only the branches already visible after authorization and filters.
      period_insights_label=QLabel('تحلیل تغییرات دوره‌ای شعب' if self.language=='fa' else 'Branch period-over-period insights')
      period_insights_label.setObjectName('title');v.addWidget(period_insights_label)
      period_insights_summary=QLabel();period_insights_summary.setWordWrap(True)
      period_insights_summary.setObjectName('metric');v.addWidget(period_insights_summary)
      period_insights_table=QTableWidget();period_insights_table.setMinimumHeight(170)
      v.addWidget(period_insights_table)
      # User-configurable management alerts, scoped to the filtered authorized branches.
      alert_controls=QHBoxLayout();v.addLayout(alert_controls)
      alert_controls.addWidget(QLabel('آستانه هشدار (مبلغ)' if self.language=='fa' else 'Alert threshold (amount)'))
      alert_threshold=QLineEdit()
      alert_threshold.setPlaceholderText('0')
      saved_threshold=str(self.settings.value(report_key+'/alert_threshold','0'))
      try:validate_threshold(saved_threshold)
      except ValueError:saved_threshold='0'
      alert_threshold.setText(saved_threshold)
      alert_controls.addWidget(alert_threshold)
      alert_summary_label=QLabel();alert_summary_label.setWordWrap(True)
      alert_summary_label.setObjectName('metric');v.addWidget(alert_summary_label)
      alert_filter_row=QHBoxLayout();v.addLayout(alert_filter_row)
      alert_filter_row.addWidget(QLabel('شدت هشدار' if self.language=='fa' else 'Alert severity'))
      alert_priority=QComboBox()
      for key,fa,en in [('all','همه','All'),('critical','بحرانی','Critical'),('high','مهم','High'),('medium','متوسط','Medium')]:
       alert_priority.addItem(fa if self.language=='fa' else en,key)
      alert_filter_row.addWidget(alert_priority)
      saved_priority=str(self.settings.value(report_key+'/alert_priority','all'))
      priority_index=alert_priority.findData(saved_priority)
      if priority_index>=0:alert_priority.setCurrentIndex(priority_index)
      def update_alert_priority():
       self.settings.setValue(report_key+'/alert_priority',alert_priority.currentData())
       refresh_branch_period_insights()

      alert_table=QTableWidget();alert_table.setMinimumHeight(150);v.addWidget(alert_table)
      def refresh_branch_period_insights():
       try:
        visible,_=authorized_filtered_comparison()
        first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
        previous_start,previous_end=previous_interval(first,last)
        with connect() as db:
         authorized=allowed_branches(db,self.user_id,self.role)
         # Resolve names against the authorized set; never query a branch outside it.
         visible_names={row['branch'] for row in visible}
         chosen=[(bid,name) for bid,name in authorized if name in visible_names]
         now={bid:cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last) for bid,_ in chosen}
         before={bid:cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=previous_start,end=previous_end) for bid,_ in chosen}
        insights={item['branch_id']:item for item in branch_period_insights(now,before)}
        period_insights_summary.setText(insight_caption(list(insights.values()),self.language))
        limit=validate_threshold(alert_threshold.text().strip() or '0')
        self.settings.setValue(report_key+'/alert_threshold',str(limit))
        warnings=categorize_alerts(evaluate_alerts(list(insights.values()),limit),limit)
        displayed_warnings=filter_alerts(warnings,alert_priority.currentData())
        names={bid:name for bid,name in chosen}
        alert_summary_label.setText(alert_summary(warnings,self.language))
        alert_table.setColumnCount(4);alert_table.setRowCount(len(displayed_warnings))
        alert_table.setHorizontalHeaderLabels(['شعبه','نوع هشدار','شدت','مبلغ'] if self.language=='fa' else ['Branch','Alert type','Severity','Amount'])
        for row_index,warning in enumerate(displayed_warnings):
         kind= ('خالص منفی' if warning['kind']=='negative' else 'افت نسبت به دوره قبل') if self.language=='fa' else ('Negative net' if warning['kind']=='negative' else 'Period decline')
         for column,value in enumerate((names.get(warning['branch_id'],''),kind,priority_label(warning['severity'],self.language),self.format_money(warning['amount']))):
          cell=QTableWidgetItem(str(value))
          if column==2:cell.setForeground(QColor({'critical':'#b91c1c','high':'#c35b65','medium':'#a16207'}[warning['severity']]))
          alert_table.setItem(row_index,column,cell)
        alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        headings=['شعبه','خالص جاری','خالص قبلی','تغییر خالص','درصد تغییر'] if self.language=='fa' else ['Branch','Current net','Previous net','Net change','Change %']
        period_insights_table.setColumnCount(5);period_insights_table.setRowCount(len(chosen));period_insights_table.setHorizontalHeaderLabels(headings)
        for ri,(bid,name) in enumerate(chosen):
         item=insights[bid]
         percent='—' if item['change_percent'] is None else f"{item['change_percent']:+.1f}%"
         for ci,value in enumerate((name,item['net'],item['previous_net'],item['change'],percent)):
          cell=QTableWidgetItem(str(value))
          if ci==3:cell.setForeground(QColor('#168b74' if item['change']>0 else '#c35b65' if item['change']<0 else '#8194a3'))
          period_insights_table.setItem(ri,ci,cell)
        period_insights_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       except (PermissionError,ValueError,sqlite3.Error,TypeError,KeyError) as exc:
        period_insights_summary.setText(str(exc));period_insights_table.setRowCount(0)
        alert_summary_label.clear();alert_table.setRowCount(0)
      refresh_insights_button=QPushButton('تحلیل تغییرات شعب' if self.language=='fa' else 'Compare Branch Periods')
      refresh_insights_button.clicked.connect(refresh_branch_period_insights);v.addWidget(refresh_insights_button)
      alert_threshold.editingFinished.connect(refresh_branch_period_insights)
      alert_priority.currentIndexChanged.connect(lambda _:update_alert_priority())
      # Monthly multi-branch trend, derived exclusively from authorized and filtered branches.
      branch_trend_title=QLabel('روند ماهانه شعب مجاز' if self.language=='fa' else 'Authorized Branch Monthly Trend')
      branch_trend_title.setObjectName('title');v.addWidget(branch_trend_title)
      branch_trend_summary=QLabel();branch_trend_summary.setWordWrap(True);v.addWidget(branch_trend_summary)
      branch_trend_chart=BranchTrendChart(self.language);v.addWidget(branch_trend_chart)
      trend_scope=QComboBox()
      trend_scope.addItem('تمام شعب قابل مشاهده' if self.language=='fa' else 'All visible branches','all')
      v.addWidget(trend_scope)
      branch_trend_table=QTableWidget();branch_trend_table.setMinimumHeight(210);v.addWidget(branch_trend_table)
      # Cache only the rows already scoped by the authorized-filtered comparison.
      trend_rows_cache=[]
      def refresh_multi_branch_trend():
       nonlocal trend_rows_cache
       try:
        records,_=authorized_filtered_comparison()
        first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
        with connect() as db:
         names={r['branch'] for r in records}
         selected=[(bid,name) for bid,name in allowed_branches(db,self.user_id,self.role) if name in names]
         data=[(name,monthly_cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)) for bid,name in selected]
        previous=trend_scope.currentData()
        trend_scope.blockSignals(True);trend_scope.clear()
        trend_scope.addItem('تمام شعب قابل مشاهده' if self.language=='fa' else 'All visible branches','all')
        for name,_ in data:trend_scope.addItem(name,name)
        idx=trend_scope.findData(previous)
        if idx>=0:trend_scope.setCurrentIndex(idx)
        trend_scope.blockSignals(False)
        scope=trend_scope.currentData()
        subset=data if scope=='all' else [(name,rows) for name,rows in data if name==scope]
        rows=merge_monthly_branches(subset)
        trend_rows_cache=rows
        branch_trend_chart.set_data(rows,self.language)
        branch_trend_summary.setText(trend_caption(rows,self.language,self.format_money))
        branch_trend_table.setColumnCount(4);branch_trend_table.setRowCount(len(rows))
        branch_trend_table.setHorizontalHeaderLabels(['ماه','دریافتی','هزینه','خالص'] if self.language=='fa' else ['Month','Receipts','Expenses','Net'])
        for ri,record in enumerate(rows):
         for ci,key in enumerate(('month','receipts','expenses','net')):
          value=record[key] if ci==0 else self.format_money(record[key])
          cell=QTableWidgetItem(str(value))
          if key=='net':cell.setForeground(QColor('#c35b65' if record[key]<0 else '#14b8a6'))
          branch_trend_table.setItem(ri,ci,cell)
        branch_trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       except (PermissionError,ValueError,sqlite3.Error,TypeError,KeyError) as exc:
        trend_rows_cache=[]
        branch_trend_chart.set_data([],self.language)
        branch_trend_summary.setText(str(exc));branch_trend_table.setRowCount(0)
      branch_trend_button=QPushButton('نمایش روند شعب' if self.language=='fa' else 'Show Branch Trend')
      branch_trend_button.clicked.connect(refresh_multi_branch_trend);v.addWidget(branch_trend_button)
      trend_scope.currentIndexChanged.connect(lambda _:refresh_multi_branch_trend())
      def export_monthly_trend():
       try:
        # Recompute before export to avoid stale data after changing filters.
        refresh_multi_branch_trend()
        if not trend_rows_cache:return
        filename,_=QFileDialog.getSaveFileName(self,'Excel','branch_monthly_trend.xlsx','Excel (*.xlsx)')
        if filename:
         if not filename.lower().endswith('.xlsx'):filename+='.xlsx'
         export_trend_excel(filename,trend_rows_cache,self.language,str(trend_scope.currentText()))
       except (OSError,ValueError,ImportError,PermissionError) as exc:
        QMessageBox.warning(self,'Export',str(exc))
      trend_excel_button=QPushButton('خروجی Excel روند ماهانه' if self.language=='fa' else 'Export Monthly Trend Excel')
      trend_excel_button.clicked.connect(export_monthly_trend);v.addWidget(trend_excel_button)
      export_filtered_excel_button=QPushButton('خروجی Excel فیلترشده' if self.language=='fa' else 'Export Filtered Excel')
      v.addWidget(export_filtered_excel_button)
      export_comparison_csv_button=QPushButton('خروجی CSV مقایسه شعب' if self.language=='fa' else 'Export Branch Comparison CSV')
      v.addWidget(export_comparison_csv_button)
      export_comparison_pdf_button=QPushButton('خروجی PDF مقایسه شعب' if self.language=='fa' else 'Export Branch Comparison PDF')
      v.addWidget(export_comparison_pdf_button)
      def export_comparison_pdf_file():
       try:
        records,_=authorized_filtered_comparison()
        filename,_=QFileDialog.getSaveFileName(self,'خروجی PDF شعب' if self.language=='fa' else 'Branch Comparison PDF','branch_cash_comparison.pdf','PDF (*.pdf)')
        if not filename:return
        filename=filename if filename.lower().endswith('.pdf') else filename+'.pdf'
        first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
        write_branch_comparison_pdf(filename,rows=records,start=first,end=last,language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,TypeError,KeyError,FileNotFoundError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      export_comparison_pdf_button.clicked.connect(export_comparison_pdf_file)
      compare_cash=QPushButton('مقایسه گردش وجوه شعب' if self.language=='fa' else 'Compare Branch Cash Movement')
      v.addWidget(compare_cash)
      cash_comparison_table=QTableWidget();v.addWidget(cash_comparison_table)
      branch_chart_title=QLabel('مقایسه تصویری شعب' if self.language=='fa' else 'Visual Branch Comparison')
      branch_chart_title.setObjectName('title');v.addWidget(branch_chart_title)
      branch_chart=QTableWidget();branch_chart.setMinimumHeight(210);v.addWidget(branch_chart)
      def refresh_cash_cards():
       bid=branch_filter.currentData()
       if bid is None:
        cash_cards.setText('');return
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       try:
        with connect() as db:
         report=cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
        cash_cards.setText('    |    '.join(f'{label}: {self.format_money(value)}' for label,value in cashflow_cards(report,self.language)))
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        cash_cards.setText(str(exc))
      def authorized_filtered_comparison():
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       with connect() as db:
        reports=[(name,cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)) for bid,name in allowed_branches(db,self.user_id,self.role)]
       visible=filter_branches(cashflow_comparison(reports,self.language),branch_search.text())
       visible=filter_financial_rows(visible,metric=metric_filter.currentData(),minimum=minimum_filter.text(),maximum=maximum_filter.text(),state=state_filter.currentData())
       ordered=sort_branch_rows(visible,sort_selector.currentData(),sort_direction.currentData())
       visible_names={row['branch'] for row in visible}
       return ordered,[(name,report) for name,report in reports if name in visible_names]
      def export_comparison_csv_file():
       try:
        records,_=authorized_filtered_comparison()
        filename,_=QFileDialog.getSaveFileName(self,'خروجی CSV شعب' if self.language=='fa' else 'Branch comparison CSV','branch_cash_comparison.csv','CSV (*.csv)')
        if not filename:return
        filename=filename if filename.lower().endswith('.csv') else filename+'.csv'
        with open(filename,'w',encoding='utf-8-sig',newline='') as output:
         # comparison_csv already includes BOM, so avoid duplicating it.
         output.write(comparison_csv(records,self.language).lstrip('\ufeff'))
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,TypeError,KeyError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      export_comparison_csv_button.clicked.connect(export_comparison_csv_file)
      def export_filtered_excel_file():
       try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter
        records,_=authorized_filtered_comparison()
        filename,_=QFileDialog.getSaveFileName(self,'خروجی Excel شعب' if self.language=='fa' else 'Filtered Branch Excel','branch_cash_filtered.xlsx','Excel Workbook (*.xlsx)')
        if not filename:return
        filename=filename if filename.lower().endswith('.xlsx') else filename+'.xlsx'
        wb=Workbook();ws=wb.active;ws.title='Branch cashflow'
        headers=['شعبه','دریافتی','هزینه','خالص گردش وجوه'] if self.language=='fa' else ['Branch','Receipts','Expenses','Net cash movement']
        ws.append(headers)
        for record in records:
         # Excel can evaluate leading formula characters in text cells.
         name=str(record['branch'])
         if name.lstrip().startswith(('=','+','-','@')) or name.startswith(('\t','\r','\n')):name="'"+name
         ws.append([name,int(record['receipts']),int(record['expenses']),int(record['net'])])
        for cell in ws[1]:
         cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17324C')
        ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
        for col,width in enumerate((35,20,20,23),1):ws.column_dimensions[get_column_letter(col)].width=width
        wb.save(filename)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,TypeError,KeyError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      export_filtered_excel_button.clicked.connect(export_filtered_excel_file)

      def load_cash_comparison():
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       try:
        records,reports=authorized_filtered_comparison()
        headers=['شعبه','دریافتی','هزینه','خالص گردش وجوه'] if self.language=='fa' else ['Branch','Receipts','Expenses','Net cash movement']
        visible_summary.setText(totals_caption(visible_totals(records),self.language,self.format_money))
        for (label_widget,value_widget),(label,value) in zip(executive_kpi_widgets,executive_labels(executive_metrics(records),self.language,self.format_money)):
         label_widget.setText(label);value_widget.setText(value)
        cash_comparison_table.setColumnCount(4);cash_comparison_table.setRowCount(len(records));cash_comparison_table.setHorizontalHeaderLabels(headers)
        for ri,record in enumerate(records):
         for ci,value in enumerate([record['branch'],record['receipts'],record['expenses'],record['net']]):
          cash_comparison_table.setItem(ri,ci,QTableWidgetItem(str(value)))
        cash_comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Branch totals are already permission-scoped above; no unfiltered SQL is used.
        bars=sort_branch_rows(comparison_bars(reports,self.language),sort_selector.currentData(),sort_direction.currentData())
        branch_chart.setColumnCount(4);branch_chart.setRowCount(len(bars))
        branch_chart.setHorizontalHeaderLabels(['شعبه','دریافتی','هزینه','خالص'] if self.language=='fa' else ['Branch','Receipts','Expenses','Net'])
        for ri,record in enumerate(bars):
         branch_chart.setItem(ri,0,QTableWidgetItem(record['branch']))
         for ci,key,color in ((1,'receipt_percent','#14b8a6'),(2,'expense_percent','#d59a42'),(3,'net_percent','#ef7474' if record['net_negative'] else '#5cb8e5')):
          progress=QProgressBar();progress.setRange(0,100);progress.setValue(record[key]);progress.setFormat(self.format_money(record[('receipts','expenses','net')[ci-1]]));progress.setTextVisible(True)
          progress.setToolTip(str(record[('receipts','expenses','net')[ci-1]]))
          progress.setStyleSheet('QProgressBar{background:#24354c;color:#ffffff;border:0;border-radius:4px;min-height:22px;text-align:center;}QProgressBar::chunk{background:'+color+';border-radius:4px;}')
          branch_chart.setCellWidget(ri,ci,progress)
        branch_chart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        branch_chart.setMinimumHeight(min(460,max(150,65+len(bars)*32)))
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        visible_summary.clear()
        for label_widget,value_widget in executive_kpi_widgets:
         label_widget.clear();value_widget.clear()
        cash_comparison_table.setRowCount(0);branch_chart.setRowCount(0)
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      # Compare the selected period against the immediately preceding period of equal length.
      finance_kpis=FinanceKpiCards(language=self.language);v.addWidget(finance_kpis)
      period_label=QLabel('مقایسه با دوره قبل' if self.language=='fa' else 'Previous-period comparison')
      period_label.setObjectName('title');v.addWidget(period_label)
      period_table=QTableWidget();period_table.setMinimumHeight(145);v.addWidget(period_table)
      def refresh_period_comparison():
       bid=branch_filter.currentData()
       if bid is None:
        period_table.setRowCount(0);return
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       try:
        with connect() as db:
         report=compare_cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
        columns=['شاخص','دوره انتخابی','دوره قبل','تغییر'] if self.language=='fa' else ['Metric','Selected period','Previous period','Change']
        finance_kpis.set_report(report,self.format_money)
        records=format_comparison(report,self.language)
        period_table.setColumnCount(4);period_table.setRowCount(len(records));period_table.setHorizontalHeaderLabels(columns)
        for ri,record in enumerate(records):
         for ci,value in enumerate(record):
          display=self.format_money(value) if ci in (1,2) else str(value)
          period_table.setItem(ri,ci,QTableWidgetItem(display))
        period_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        period_table.setRowCount(0);finance_kpis.clear()
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      period_refresh=QPushButton('مقایسه با دوره قبل' if self.language=='fa' else 'Compare Previous Period')
      v.addWidget(period_refresh);period_refresh.clicked.connect(refresh_period_comparison)
      # Monthly receipts/expenses visual comparison, scoped to the selected branch.
      trend_title=QLabel('روند ماهانه گردش وجوه' if self.language=='fa' else 'Monthly Cash Movement Trend')
      trend_title.setObjectName('title');v.addWidget(trend_title)
      trend_button=QPushButton('نمایش روند ماهانه' if self.language=='fa' else 'Show Monthly Trend')
      v.addWidget(trend_button)
      interactive_chart=CashflowChart(language=self.language);v.addWidget(interactive_chart)
      trend_table=QTableWidget();trend_table.setMinimumHeight(230);v.addWidget(trend_table)
      def refresh_monthly_trend():
       bid=branch_filter.currentData()
       if bid is None:
        trend_table.setRowCount(0);return
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       try:
        with connect() as db:
         rows=scale_bars(monthly_cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last))
        interactive_chart.set_rows(rows)
        labels=['ماه','دریافتی','هزینه','خالص','مقایسه دریافتی / هزینه'] if self.language=='fa' else ['Month','Receipts','Expenses','Net','Receipts / expenses']
        trend_table.setColumnCount(5);trend_table.setRowCount(len(rows));trend_table.setHorizontalHeaderLabels(labels)
        for ri,record in enumerate(rows):
         for ci,value in enumerate((record['month'],record['receipts'],record['expenses'],record['net'])):
          trend_table.setItem(ri,ci,QTableWidgetItem(str(value)))
         bar=QWidget();line=QHBoxLayout(bar);line.setContentsMargins(4,2,4,2)
         for key,color in [('receipt_percent','#14b8a6'),('expense_percent','#d59a42')]:
          progress=QProgressBar();progress.setRange(0,100);progress.setValue(record[key]);progress.setTextVisible(False)
          progress.setStyleSheet('QProgressBar{background:#24354c;border:0;border-radius:4px;min-height:11px;}QProgressBar::chunk{background:'+color+';border-radius:4px;}')
          line.addWidget(progress)
         trend_table.setCellWidget(ri,4,bar)
        trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        interactive_chart.set_rows([])
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      trend_button.clicked.connect(refresh_monthly_trend)
      compare_cash.clicked.connect(load_cash_comparison)
      compare_cash.clicked.connect(refresh_branch_period_insights)
      branch_search.textChanged.connect(lambda _:load_cash_comparison())
      metric_filter.currentIndexChanged.connect(lambda _:load_cash_comparison())
      state_filter.currentIndexChanged.connect(lambda _:load_cash_comparison())
      minimum_filter.editingFinished.connect(load_cash_comparison)
      maximum_filter.editingFinished.connect(load_cash_comparison)
      sort_selector.currentIndexChanged.connect(lambda _:load_cash_comparison())
      sort_direction.currentIndexChanged.connect(lambda _:load_cash_comparison())
      branch_filter.currentIndexChanged.connect(lambda _:refresh_cash_cards())
      start.dateChanged.connect(lambda _:refresh_cash_cards())
      end.dateChanged.connect(lambda _:refresh_cash_cards())
      finance_controls=QHBoxLayout();v.addLayout(finance_controls)
      cash_button=QPushButton('گردش وجوه شعبه Excel' if self.language=='fa' else 'Branch Cash Movement Excel')
      finance_controls.addWidget(cash_button)
      def export_cash_report():
       bid=branch_filter.currentData()
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       if bid is None:return
       filename,_=QFileDialog.getSaveFileName(self,'گزارش گردش وجوه' if self.language=='fa' else 'Cash movement','branch_cash_movement.xlsx','Excel Workbook (*.xlsx)')
       if not filename:return
       try:
        with connect() as db:
         result=cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
        export_cashflow(filename if filename.lower().endswith('.xlsx') else filename+'.xlsx',result,start=first,end=last,branch_name=branch_filter.currentText(),language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش ذخیره شد.' if self.language=='fa' else 'Report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      cash_button.clicked.connect(export_cash_report)
      pdf_button=QPushButton('گزارش مدیریتی PDF' if self.language=='fa' else 'Management PDF Report')
      finance_controls.addWidget(pdf_button)
      def export_management_pdf():
       bid=branch_filter.currentData()
       if bid is None:return
       first=start.date().toString('yyyy-MM-dd');last=end.date().addDays(1).toString('yyyy-MM-dd')
       filename,_=QFileDialog.getSaveFileName(self,'گزارش مدیریتی PDF' if self.language=='fa' else 'Management PDF Report',f'branch_{bid}_management.pdf','PDF (*.pdf)')
       if not filename:return
       try:
        with connect() as db:
         report=cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
         comparison=compare_cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
         months=monthly_cashflow(db,branch_id=bid,user_id=self.user_id,role=self.role,start=first,end=last)
        write_cashflow_pdf(filename if filename.lower().endswith('.pdf') else filename+'.pdf',branch_name=branch_filter.currentText(),start=first,end=last,report=report,comparison=comparison,monthly=months,language=self.language)
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','گزارش PDF ذخیره شد.' if self.language=='fa' else 'PDF report saved.')
       except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError,FileNotFoundError) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      pdf_button.clicked.connect(export_management_pdf)
      expense_button=QPushButton('ثبت هزینه شعبه' if self.language=='fa' else 'Record Branch Expense')
      finance_controls.addWidget(expense_button)
      def add_branch_expense():
       bid=branch_filter.currentData()
       if bid is None:return
       title='ثبت هزینه شعبه' if self.language=='fa' else 'Record branch expense'
       category,ok=QInputDialog.getText(self,title,'دسته هزینه' if self.language=='fa' else 'Expense category')
       if not ok:return
       amount,ok=QInputDialog.getInt(self,title,'مبلغ (تومان)' if self.language=='fa' else 'Amount (Toman)',1,1,2000000000)
       if not ok:return
       description,ok=QInputDialog.getText(self,title,'شرح (اختیاری)' if self.language=='fa' else 'Description (optional)')
       if not ok:return
       try:
        with connect() as db:
         record_expense(db,branch_id=bid,user_id=self.user_id,role=self.role,category=category,description=description,amount=amount,spent_on=date.today().isoformat())
        refresh_cash_cards()
        QMessageBox.information(self,'موفق' if self.language=='fa' else 'Success','هزینه ثبت شد.' if self.language=='fa' else 'Expense saved.')
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        QMessageBox.warning(self,'خطا' if self.language=='fa' else 'Error',str(exc))
      expense_button.clicked.connect(add_branch_expense)
      if branch_filter.count():load_branch_report();refresh_cash_cards();refresh_monthly_trend();refresh_period_comparison()
     elif i==23:
      w,v=self.page('مدیریت شعب هتل')
      v.addWidget(QLabel('مرحله نخست چندشعبه‌ای: تعریف شعب و تخصیص اتاق؛ تفکیک کامل رزروها و دسترسی کاربران در مراحل بعد.'))
      form=QFormLayout();branch_name=QLineEdit();branch_city=QLineEdit();branch_address=QLineEdit();branch_phone=QLineEdit()
      for label,field in [('نام شعبه',branch_name),('شهر',branch_city),('آدرس',branch_address),('تلفن',branch_phone)]:form.addRow(label,field)
      v.addLayout(form);save=QPushButton('افزودن شعبه');save.setObjectName('primary');v.addWidget(save)
      branches_table=QTableWidget();v.addWidget(branches_table)
      v.addWidget(QLabel('تخصیص اتاق به شعبه'))
      selectors=QHBoxLayout();room_select=QComboBox();branch_select=QComboBox()
      for rid,number in c.execute('SELECT id,number FROM rooms ORDER BY number'):room_select.addItem(str(number),rid)
      selectors.addWidget(room_select);selectors.addWidget(branch_select)
      assign=QPushButton('ثبت تخصیص');selectors.addWidget(assign);v.addLayout(selectors)
      def refresh_branches():
       with connect() as db:rows=db.execute('SELECT id,name,city,address,phone,active FROM branches ORDER BY id').fetchall()
       branches_table.setRowCount(len(rows));branches_table.setColumnCount(6)
       branches_table.setHorizontalHeaderLabels(['شناسه','شعبه','شهر','آدرس','تلفن','فعال'])
       for r,values in enumerate(rows):
        for col,value in enumerate(values):branches_table.setItem(r,col,QTableWidgetItem(str(value)))
       branches_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       branch_select.clear()
       for bid,name,_,_,_,active in rows:
        if active:branch_select.addItem(name,bid)
      def save_branch():
       try:
        with connect() as db:add_branch(db,branch_name.text(),branch_city.text(),branch_address.text(),branch_phone.text())
        audit(self.username,'branch_added',branch_name.text());refresh_branches()
       except (ValueError,sqlite3.IntegrityError) as exc:QMessageBox.warning(self,'خطا',str(exc))
      def save_assignment():
       try:
        with connect() as db:transfer_room(db,room_select.currentData(),branch_select.currentData())
        audit(self.username,'room_branch_assigned',f'{room_select.currentData()} -> {branch_select.currentData()}')
        QMessageBox.information(self,'موفق','شعبه اتاق به‌روزرسانی شد.')
       except (ValueError,sqlite3.Error) as exc:QMessageBox.warning(self,'خطا',str(exc))
      save.clicked.connect(save_branch);assign.clicked.connect(save_assignment);refresh_branches()
     elif i==21:
      w,v=self.page('مدیریت نرخ‌های فصلی')
      v.addWidget(QLabel('قوانین نرخ‌گذاری برای رزروهای جدید قابل محاسبه‌اند؛ قیمت رزروهای موجود خودکار تغییر نمی‌کند.'))
      form=QHBoxLayout();kind=QComboBox();kind.addItems(['همه','استاندارد','سوئیت']);form.addWidget(kind)
      begin=QDateEdit();begin.setCalendarPopup(True);begin.setDate(QDate.currentDate());form.addWidget(begin)
      end=QDateEdit();end.setCalendarPopup(True);end.setDate(QDate.currentDate().addDays(7));form.addWidget(end)
      pct=QSpinBox();pct.setRange(50,300);pct.setValue(120);pct.setSuffix('٪');form.addWidget(pct)
      add=QPushButton('ثبت قانون');form.addWidget(add);v.addLayout(form)
      listing=QTableWidget();v.addWidget(listing)
      def reload_rules():
       with connect() as db: rows=db.execute('SELECT id,room_kind,start_date,end_date,multiplier_percent FROM seasonal_rates ORDER BY id DESC').fetchall()
       listing.setRowCount(len(rows));listing.setColumnCount(5);listing.setHorizontalHeaderLabels(['شناسه','نوع اتاق','شروع','پایان','درصد نرخ پایه'])
       for row_i,row in enumerate(rows):
        for col_i,value in enumerate(row): listing.setItem(row_i,col_i,QTableWidgetItem(str(value)))
       listing.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
      def save_rule():
       a,b=begin.date().toString('yyyy-MM-dd'),end.date().toString('yyyy-MM-dd')
       if b<=a: QMessageBox.warning(self,'تاریخ نامعتبر','تاریخ پایان باید پس از شروع باشد.');return
       with connect() as db: db.execute('INSERT INTO seasonal_rates(room_kind,start_date,end_date,multiplier_percent) VALUES(?,?,?,?)',(kind.currentText(),a,b,pct.value()))
       audit(self.username,'seasonal_rate_added',f'{kind.currentText()} {a} {b} {pct.value()}')
       reload_rules()
      add.clicked.connect(save_rule);reload_rules()
     elif i==22:
      w,v=self.page('اعلان‌های پذیرش')
      with connect() as db:
       departures=upcoming_departures(db,date.today().isoformat(),2)
       low_stock=db.execute('SELECT name,quantity,minimum FROM inventory WHERE quantity<=minimum ORDER BY name').fetchall()
      v.addWidget(QLabel('خروج مهمانان تا دو روز آینده'))
      v.addWidget(self.table(['رزرو','مهمان','اتاق','تاریخ خروج'],departures))
      v.addWidget(QLabel('هشدار موجودی انبار'))
      v.addWidget(self.table(['کالا','موجودی','حداقل'],low_stock))
     elif i==20:
      w,v=self.page('نقشه تصویری اشغال اتاق‌ها' if self.language=='fa' else 'Room availability calendar')
      from occupancy_calendar import cell_description, cell_color, is_bookable
      fa=self.language=='fa'
      controls=QHBoxLayout()
      controls.addWidget(QLabel('شروع بازه:' if fa else 'Start date:'))
      start_picker=QDateEdit();start_picker.setCalendarPopup(True);start_picker.setDisplayFormat('yyyy-MM-dd');start_picker.setDate(QDate.currentDate());controls.addWidget(start_picker)
      controls.addWidget(QLabel('نمایش:' if fa else 'View:'))
      view_mode=QComboBox();view_mode.addItem('هفتگی' if fa else 'Week',7);view_mode.addItem('دو هفته' if fa else 'Two weeks',14);view_mode.addItem('ماهانه (۳۰ روز)' if fa else 'Month (30 days)',30);view_mode.setCurrentIndex(1);controls.addWidget(view_mode)
      controls.addWidget(QLabel('تعداد روز:' if fa else 'Days:'))
      duration=QSpinBox();duration.setRange(7,30);duration.setValue(14);controls.addWidget(duration)
      refresh=QPushButton('نمایش نقشه' if fa else 'Refresh calendar');refresh.setObjectName('primary');controls.addWidget(refresh)
      v.addLayout(controls)
      legend=QLabel(('🟢 آزاد   🟠 رزرو شده   🔴 پذیرش شده  |  برای ثبت رزرو روی خانه آزاد دوبار کلیک کنید' if fa else '🟢 Available   🟠 Reserved   🔴 Checked in  |  Double-click an available cell to book'))
      legend.setWordWrap(True);v.addWidget(legend)
      info=QLabel();v.addWidget(info)
      grid_table=QTableWidget();grid_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
      grid_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
      grid_table.setMinimumHeight(480);grid_table.setAlternatingRowColors(True);v.addWidget(grid_table)
      current={'rooms':[], 'dates':[], 'cells':{}, 'bookings':[]}
      def draw_grid():
       with connect() as db:
        rooms=db.execute("SELECT id,number FROM rooms WHERE status='فعال' AND branch_id=? ORDER BY number",(self.active_branch,)).fetchall()
        bookings=db.execute("SELECT r.room_id,r.checkin,r.checkout,r.status FROM reservations r JOIN rooms ro ON ro.id=r.room_id WHERE ro.branch_id=? AND r.checkout>? AND r.checkin<?",(self.active_branch,start_picker.date().toString('yyyy-MM-dd'),start_picker.date().addDays(duration.value()).toString('yyyy-MM-dd'))).fetchall()
       dates,cells=build_grid(rooms,bookings,start_picker.date().toString('yyyy-MM-dd'),duration.value())
       current.update(rooms=rooms,dates=dates,cells=cells,bookings=bookings)
       summary=occupancy_summary(cells,len(dates))
       if fa:info.setText(f"اشغال: {summary['occupancy_percent']}٪ | شب‌اتاق اشغال: {summary['occupied_room_nights']} | شب‌اتاق آزاد: {summary['available_room_nights']}")
       else:info.setText(f"Occupancy: {summary['occupancy_percent']}% | Occupied room-nights: {summary['occupied_room_nights']} | Available room-nights: {summary['available_room_nights']}")
       grid_table.setRowCount(len(rooms));grid_table.setColumnCount(len(dates)+1)
       grid_table.setHorizontalHeaderLabels([('اتاق' if fa else 'Room')]+[self.format_date(day.isoformat()) for day in dates]);grid_table.setColumnWidth(0,95)
       for row,(room_id,number) in enumerate(rooms):
        room_cell=QTableWidgetItem(str(number));room_cell.setFlags(room_cell.flags() & ~Qt.ItemFlag.ItemIsEditable);grid_table.setItem(row,0,room_cell)
        for j,state in enumerate(cells[room_id]):
         cell=QTableWidgetItem(cell_description(state,self.language));cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
         cell.setBackground(QColor(cell_color(state)));cell.setForeground(QColor('#ffffff'))
         cell.setToolTip(f"{number} | {dates[j].isoformat()} | {cell_description(state,self.language)}")
         grid_table.setItem(row,j+1,cell)
       for j in range(1,len(dates)+1):grid_table.setColumnWidth(j,112)
      def select_slot(row,col):
       if col<1 or row<0 or row>=len(current['rooms']) or col>len(current['dates']):return
       room_id,number=current['rooms'][row]
       selected=current['dates'][col-1]
       if not is_bookable(current['cells'][room_id][col-1]):
        QMessageBox.information(self,'اتاق اشغال است' if fa else 'Room unavailable','این اتاق در تاریخ انتخاب‌شده آزاد نیست.' if fa else 'This room is not available on the selected date.');return
       dialog=BookingDialog(self)
       idx=dialog.room.findData(room_id)
       if idx<0:return
       dialog.room.setCurrentIndex(idx)
       dialog.start.setDate(QDate(selected.year,selected.month,selected.day))
       next_day=selected.fromordinal(selected.toordinal()+1)
       dialog.end.setDate(QDate(next_day.year,next_day.month,next_day.day))
       if dialog.exec():draw_grid()
      def show_slot_details(row,col):
       if col<1 or row<0 or row>=len(current['rooms']) or col>len(current['dates']):return
       room_id,number=current['rooms'][row]
       day=current['dates'][col-1].isoformat()
       state=current['cells'][room_id][col-1]
       from occupancy_calendar import matching_bookings
       matches=matching_bookings(current['bookings'],room_id,day)
       title=('جزئیات وضعیت اتاق' if fa else 'Room availability details')
       detail=(f'اتاق: {number}\nتاریخ: {day}\nوضعیت: {cell_description(state,self.language)}' if fa else f'Room: {number}\nDate: {day}\nStatus: {cell_description(state,self.language)}')
       for booking in matches:
        detail+=f'\n{booking[1]} → {booking[2]} | {booking[3]}'
       QMessageBox.information(self,title,detail)
      view_mode.currentIndexChanged.connect(lambda _:duration.setValue(view_mode.currentData()))
      refresh.clicked.connect(draw_grid)
      start_picker.dateChanged.connect(lambda _:draw_grid())
      duration.valueChanged.connect(lambda _:draw_grid())
      grid_table.cellClicked.connect(show_slot_details)
      def transfer_from_calendar():
       row=grid_table.currentRow();col=grid_table.currentColumn()
       if col<1 or row<0 or row>=len(current['rooms']) or col>len(current['dates']):
        QMessageBox.information(self,'انتخاب' if fa else 'Selection','ابتدا یک خانه رزرو شده انتخاب کنید.' if fa else 'Select a reserved cell first.');return
       source_room,_=current['rooms'][row]
       selected_date=current['dates'][col-1].isoformat()
       with connect() as db:
        bookings=db.execute("""SELECT r.id,g.name,r.checkin,r.checkout FROM reservations r
          JOIN guests g ON g.id=r.guest_id WHERE r.room_id=? AND r.branch_id=?
          AND r.status='رزرو شده' AND r.checkin<=? AND r.checkout>?""",
          (source_room,self.active_branch,selected_date,selected_date)).fetchall()
       if not bookings:
        QMessageBox.information(self,'انتقال رزرو' if fa else 'Transfer reservation','رزرو قابل انتقالی در این خانه وجود ندارد.' if fa else 'No transferable booking in this cell.');return
       dialog=QDialog(self);dialog.setWindowTitle('انتقال رزرو' if fa else 'Transfer reservation')
       dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
       form=QFormLayout(dialog);form.setSpacing(12)
       reservation_picker=QComboBox()
       for rid,name,start,end in bookings:reservation_picker.addItem(f'#{rid} • {name} • {start} → {end}',rid)
       destination=QComboBox()
       for room_id,number in current['rooms']:
        if room_id!=source_room:destination.addItem(str(number),room_id)
       form.addRow('رزرو' if fa else 'Reservation',reservation_picker)
       form.addRow('اتاق مقصد' if fa else 'Destination room',destination)
       hint=QLabel('');hint.setWordWrap(True);form.addRow(hint)
       confirm=QPushButton('تأیید انتقال' if fa else 'Confirm transfer');confirm.setObjectName('primary');form.addRow(confirm)
       def perform_transfer():
        if destination.currentData() is None:return
        question=('آیا انتقال این رزرو به اتاق انتخاب‌شده تأیید می‌شود؟' if fa else 'Move this reservation to the selected room?')
        if QMessageBox.question(dialog,'تأیید' if fa else 'Confirm',question)!=QMessageBox.StandardButton.Yes:return
        try:
         from room_transfer import transfer_booking
         with connect() as db:
          transfer_booking(db,user_id=self.user_id,role=self.role,branch_id=self.active_branch,
           reservation_id=reservation_picker.currentData(),destination_room_id=destination.currentData(),actor=self.username)
         dialog.accept();draw_grid()
        except (PermissionError,ValueError,RuntimeError,sqlite3.Error) as exc:hint.setText(str(exc))
       confirm.clicked.connect(perform_transfer)
       dialog.exec()
      transfer_button=QPushButton('انتقال رزرو انتخاب‌شده' if fa else 'Transfer selected reservation')
      transfer_button.clicked.connect(transfer_from_calendar);v.addWidget(transfer_button)
      def show_transfer_history():
       from room_transfer_history import query_transfers, export_transfers_csv
       from room_transfer_analytics import summarize_transfers, export_transfers_excel
       from transfer_date_locale import normalize_report_date, report_date
       from transfer_pdf_report import export_transfers_pdf
       dialog=QDialog(self);dialog.setWindowTitle('تاریخچه انتقال اتاق‌ها' if fa else 'Room transfer history')
       dialog.resize(920,580)
       dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
       layout=QVBoxLayout(dialog)
       filters=QHBoxLayout();reservation_filter=QLineEdit();reservation_filter.setPlaceholderText('شماره رزرو' if fa else 'Reservation ID')
       actor_filter=QLineEdit();actor_filter.setPlaceholderText('کاربر' if fa else 'Actor')
       filters.addWidget(reservation_filter);filters.addWidget(actor_filter)
       date_from=QDateEdit();date_from.setCalendarPopup(True);date_from.setDisplayFormat('yyyy-MM-dd');date_from.setDate(QDate.currentDate().addYears(-1))
       date_to=QDateEdit();date_to.setCalendarPopup(True);date_to.setDisplayFormat('yyyy-MM-dd');date_to.setDate(QDate.currentDate())
       filters.addWidget(date_from);filters.addWidget(date_to);layout.addLayout(filters)
       localized_dates=QHBoxLayout()
       local_start=QLineEdit();local_end=QLineEdit()
       local_start.setPlaceholderText('از تاریخ شمسی (۱۴۰۵-۰۱-۰۱)' if fa else 'From Gregorian (YYYY-MM-DD)')
       local_end.setPlaceholderText('تا تاریخ شمسی (۱۴۰۵-۱۲-۲۹)' if fa else 'To Gregorian (YYYY-MM-DD)')
       localized_dates.addWidget(local_start);localized_dates.addWidget(local_end)
       layout.addLayout(localized_dates)
       layout.addWidget(QLabel('در صورت وارد کردن تاریخ متنی، بر فیلتر تقویم اولویت دارد.' if fa else 'Typed dates override the calendar filters.'))
       summary_label=QLabel();summary_label.setWordWrap(True);layout.addWidget(summary_label)
       table=self.table(['شناسه','زمان','رزرو','اتاق مبدأ','اتاق مقصد','کاربر'] if fa else ['ID','Time','Reservation','From room','To room','Actor'],[])
       layout.addWidget(table)
       # Analytics are computed from the exact same authorized and filtered rows.
       from transfer_dashboard import build_transfer_dashboard
       analytics_panel=QFrame();analytics_panel.setObjectName('transferAnalyticsPanel')
       analytics_layout=QVBoxLayout(analytics_panel)
       analytics_title=QLabel('تحلیل انتقال اتاق‌ها' if fa else 'Room transfer insights')
       analytics_title.setStyleSheet('font-weight:700;font-size:15px;')
       analytics_layout.addWidget(analytics_title)
       analytics_tabs=QTabWidget()
       analytics_tables=[]
       for heading in (['روند ماهانه','کاربران فعال','اتاق‌های مبدأ','اتاق‌های مقصد'] if fa else ['Monthly trend','Active staff','Source rooms','Destination rooms']):
        panel=QWidget();panel_layout=QVBoxLayout(panel)
        data_table=QTableWidget(0,3);data_table.setHorizontalHeaderLabels(['عنوان','تعداد','نمودار' ] if fa else ['Label','Count','Chart'])
        data_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        data_table.setAlternatingRowColors(True)
        data_table.horizontalHeader().setStretchLastSection(True)
        panel_layout.addWidget(data_table);analytics_tabs.addTab(panel,heading)
        analytics_tables.append(data_table)
       analytics_layout.addWidget(analytics_tabs)
       layout.addWidget(analytics_panel)
       def refresh_analytics(rows):
        from PySide6.QtWidgets import QProgressBar
        data=build_transfer_dashboard(rows)
        for widget,key in zip(analytics_tables,('monthly','actors','sources','destinations')):
         items=data[key];widget.setRowCount(len(items))
         maximum=max((count for _,count in items),default=1)
         for ri,(label,count) in enumerate(items):
          widget.setItem(ri,0,QTableWidgetItem(str(label)))
          widget.setItem(ri,1,QTableWidgetItem(str(count)))
          bar=QProgressBar();bar.setRange(0,maximum);bar.setValue(count)
          bar.setTextVisible(False);bar.setMinimumHeight(14)
          widget.setCellWidget(ri,2,bar)
       def show_branch_comparison():
        from transfer_branch_comparison import compare_transfers, export_comparison_csv
        from transfer_executive_dashboard import dashboard
        window=QDialog(dialog)
        window.setWindowTitle('داشبورد مدیریتی شعب' if fa else 'Executive branch dashboard')
        window.resize(980,620)
        window.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        body=QVBoxLayout(window)
        heading=QLabel('تحلیل مقایسه‌ای انتقال رزروها' if fa else 'Room transfer performance by branch')
        heading.setStyleSheet('font-size:19px;font-weight:700;padding:8px;')
        body.addWidget(heading)
        controls=QHBoxLayout()
        branch_search=QLineEdit();branch_search.setPlaceholderText('جستجوی نام شعبه' if fa else 'Search branches')
        metric=QComboBox()
        metrics=[('انتقال‌ها' if fa else 'Transfers','transfers'),('رزروها' if fa else 'Reservations','reservations'),
                 ('اتاق‌های مبدأ' if fa else 'Source rooms','source_rooms'),('اتاق‌های مقصد' if fa else 'Destination rooms','destination_rooms'),
                 ('کارکنان فعال' if fa else 'Active staff','active_staff')]
        for label,key in metrics:metric.addItem(label,key)
        order=QComboBox();order.addItem('بیشترین به کمترین' if fa else 'High to low',True)
        order.addItem('کمترین به بیشترین' if fa else 'Low to high',False)
        controls.addWidget(branch_search);controls.addWidget(metric);controls.addWidget(order);body.addLayout(controls)
        cards=QHBoxLayout()
        labels=['شعب','انتقال‌ها','رزروهای یکتا در هر شعبه','کارکنان به تفکیک شعبه'] if fa else ['Branches','Transfers','Branch-level unique bookings','Branch-level active staff']
        card_widgets=[]
        for label in labels:
         box=QFrame();box.setObjectName('metricCard');box.setStyleSheet('QFrame#metricCard{background:#142a43;border:1px solid #36516f;border-radius:12px;padding:8px;}')
         layout_box=QVBoxLayout(box);caption=QLabel(label);caption.setWordWrap(True)
         value=QLabel('0');value.setStyleSheet('font-size:23px;font-weight:700;color:#2bd0bf;')
         layout_box.addWidget(caption);layout_box.addWidget(value);cards.addWidget(box);card_widgets.append(value)
        body.addLayout(cards)
        results=self.table(['رتبه','شعبه','انتقال','رزروهای یکتا','اتاق مبدأ','اتاق مقصد','کارکنان فعال','کاربر پرتکرار','مقایسه'] if fa else
                           ['Rank','Branch','Transfers','Unique bookings','Source rooms','Destination rooms','Active staff','Top actor','Comparison'],[])
        body.addWidget(results)
        buttons=QHBoxLayout();refresh=QPushButton('به‌روزرسانی' if fa else 'Refresh')
        export=QPushButton('خروجی CSV' if fa else 'Export CSV')
        buttons.addWidget(refresh);buttons.addWidget(export);body.addLayout(buttons)
        comparison=[];displayed=[]
        def render():
         view=dashboard(comparison,search=branch_search.text(),order=metric.currentData(),descending=order.currentData())
         displayed[:]=view['rows'];totals=view['totals']
         for widget,key in zip(card_widgets,('branches','transfers','reservations','active_staff_by_branch')):
          widget.setText(str(totals[key]))
         results.setRowCount(len(displayed))
         for ri,item in enumerate(displayed):
          for ci,key in enumerate(('rank','branch','transfers','reservations','source_rooms','destination_rooms','active_staff','top_actor')):
           results.setItem(ri,ci,QTableWidgetItem(str(item[key])))
          bar=QProgressBar();bar.setRange(0,100);bar.setValue(item['bar_percent']);bar.setFormat(str(item[metric.currentData()]))
          results.setCellWidget(ri,8,bar)
        def load():
         try:
          start=normalize_report_date(local_start.text(),self.language) if local_start.text().strip() else date_from.date().toString('yyyy-MM-dd')
          end=normalize_report_date(local_end.text(),self.language) if local_end.text().strip() else date_to.date().toString('yyyy-MM-dd')
          with connect() as db:
           comparison[:]=compare_transfers(db,user_id=self.user_id,role=self.role,date_from=start,date_to=end)
          render()
         except (PermissionError,ValueError,sqlite3.Error) as exc:
          QMessageBox.warning(window,'خطا' if fa else 'Error',str(exc))
        def save():
         if not displayed:return
         path,_=QFileDialog.getSaveFileName(window,'CSV','branch_transfer_comparison.csv','CSV Files (*.csv)')
         if path:
          try:export_comparison_csv(path,displayed)
          except OSError as exc:QMessageBox.warning(window,'خطا' if fa else 'Error',str(exc))
        refresh.clicked.connect(load);export.clicked.connect(save)
        branch_search.textChanged.connect(lambda _:render());metric.currentIndexChanged.connect(lambda _:render());order.currentIndexChanged.connect(lambda _:render())
        load();window.exec()
       compare_button=QPushButton('داشبورد شعب' if fa else 'Branch dashboard')
       compare_button.clicked.connect(show_branch_comparison)
       footer=QHBoxLayout();refresh_history=QPushButton('جستجو' if fa else 'Search');export_history=QPushButton('خروجی CSV' if fa else 'Export CSV')
       export_excel=QPushButton('خروجی Excel' if fa else 'Export Excel')
       export_pdf=QPushButton('خروجی PDF' if fa else 'Export PDF')
       footer.addWidget(refresh_history);footer.addWidget(export_history);footer.addWidget(export_excel);footer.addWidget(export_pdf);footer.addWidget(compare_button);layout.addLayout(footer)
       records=[]
       def reload_history():
        raw=reservation_filter.text().strip()
        if raw and (not raw.isascii() or not raw.isdecimal() or int(raw)<1):
         QMessageBox.warning(dialog,'خطا' if fa else 'Error','شماره رزرو نامعتبر است.' if fa else 'Invalid reservation ID.');return
        try:
         start=normalize_report_date(local_start.text(),self.language) if local_start.text().strip() else date_from.date().toString('yyyy-MM-dd')
         end=normalize_report_date(local_end.text(),self.language) if local_end.text().strip() else date_to.date().toString('yyyy-MM-dd')
         if start>end:raise ValueError('Start date exceeds end date')
        except ValueError as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc));return
        with connect() as db:
         rows=query_transfers(db,branch_id=self.active_branch,reservation_id=int(raw) if raw else None,actor=actor_filter.text().strip(),date_from=start,date_to=end)
        records[:]=rows
        refresh_analytics(rows)
        stats=summarize_transfers(rows)
        popular=next(iter(stats['by_source']), '—')
        summary_label.setText((f'تعداد انتقال‌ها: {stats["total"]} | پرتکرارترین اتاق مبدأ: {popular}' if fa else f'Transfers: {stats["total"]} | Most transferred from: {popular}'))
        table.setRowCount(len(rows))
        for ri,record in enumerate(rows):
         for ci,value in enumerate(record):table.setItem(ri,ci,QTableWidgetItem(str(value)))
       def save_history():
        if not records:
         QMessageBox.information(dialog,'گزارش' if fa else 'Report','داده‌ای برای خروجی وجود ندارد.' if fa else 'No records to export.');return
        path,_=QFileDialog.getSaveFileName(dialog,'CSV','room_transfers.csv','CSV Files (*.csv)')
        if path:export_transfers_csv(path,records)
       def save_excel():
        if not records:
         QMessageBox.information(dialog,'گزارش' if fa else 'Report','داده‌ای برای خروجی وجود ندارد.' if fa else 'No records to export.');return
        path,_=QFileDialog.getSaveFileName(dialog,'Excel','room_transfers.xlsx','Excel Files (*.xlsx)')
        if path:
         try:export_transfers_excel(path,records,language=self.language)
         except (OSError,ValueError,ImportError) as exc:QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       def save_pdf():
        if not records:
         QMessageBox.information(dialog,'گزارش' if fa else 'Report','داده‌ای برای خروجی وجود ندارد.' if fa else 'No records to export.');return
        path,_=QFileDialog.getSaveFileName(dialog,'PDF','room_transfers.pdf','PDF Files (*.pdf)')
        if path:
         try:export_transfers_pdf(path,records,language=self.language)
         except (OSError,ValueError,ImportError) as exc:QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       refresh_history.clicked.connect(reload_history);export_history.clicked.connect(save_history);export_excel.clicked.connect(save_excel);export_pdf.clicked.connect(save_pdf)
       reload_history();dialog.exec()
      history_button=QPushButton('تاریخچه انتقال اتاق‌ها' if fa else 'Room transfer history')
      history_button.clicked.connect(show_transfer_history);v.addWidget(history_button)
      grid_table.cellDoubleClicked.connect(select_slot)
      draw_grid()
     elif i==0:
      w,v=self.page('Management dashboard • Active branch' if self.language=='en' else 'داشبورد مدیریتی • نمای شعبه فعال')
      from analytics import occupancy_rate
      from dashboard_metrics import summarize_dashboard
      from responsive_dashboard import ResponsiveDashboardGrid
      today=date.today().isoformat()
      # Every dashboard query is scoped to the authorized active branch.
      rooms=c.execute("SELECT COUNT(*) FROM rooms WHERE branch_id=? AND status='فعال'",(self.active_branch,)).fetchone()[0]
      active=c.execute("SELECT COUNT(*) FROM reservations WHERE branch_id=? AND status='پذیرش شده' AND checkin<=? AND checkout>?",(self.active_branch,today,today)).fetchone()[0]
      bookings=c.execute("SELECT COUNT(*) FROM reservations WHERE branch_id=? AND status='رزرو شده'",(self.active_branch,)).fetchone()[0]
      income=c.execute('SELECT COALESCE(SUM(p.amount),0) FROM payments p JOIN reservations r ON r.id=p.reservation_id WHERE r.branch_id=?',(self.active_branch,)).fetchone()[0]
      kpis=summarize_dashboard(rooms,active,bookings,income)
      subtitle=QLabel(('Branch overview: ' if self.language=='en' else 'خلاصه عملکرد شعبه «')+self.branch_picker.currentText()+('  |  ' if self.language=='en' else '»  |  ')+self.format_date(today));subtitle.setObjectName('subtitle');v.addWidget(subtitle)
      # Responsive KPI grid: 3 columns on normal windows, 2 on narrower screens.
      metric_items=[
       ('اتاق‌های فعال' if self.language=='fa' else 'Active rooms',kpis['rooms']),
       ('اشغال امروز' if self.language=='fa' else 'Occupied today',kpis['occupied']),
       ('درصد اشغال' if self.language=='fa' else 'Occupancy rate',f"{kpis['occupancy_percent']:.1f}%"),
       ('رزروهای در انتظار' if self.language=='fa' else 'Pending bookings',kpis['pending']),
       ('دریافتی شعبه' if self.language=='fa' else 'Branch receipts',self.format_money(kpis['income']))]
      metric_cards=[]
      for label,value in metric_items:
       card=QFrame();card.setObjectName('dashboardCard')
       card_layout=QVBoxLayout(card);card_layout.setContentsMargins(18,15,18,15);card_layout.setSpacing(8)
       caption=QLabel(label);caption.setObjectName('dashboardCardLabel');caption.setWordWrap(True)
       number=QLabel(str(value));number.setObjectName('dashboardCardValue');number.setWordWrap(True)
       card_layout.addWidget(caption);card_layout.addWidget(number)
       card.setMinimumHeight(104);card.setMinimumWidth(0);metric_cards.append(card)
      summary_panel=ResponsiveDashboardGrid(metric_cards)
      v.addWidget(summary_panel)
      if self.role=='admin' and self.user_id is not None:
       try:
        from security_notifications_v114 import unread_count
        from operation_guard import authorize_action
        authorize_action(c,self.user_id,self.session_token,'security.view')
        pending_alerts=unread_count(c,self.user_id)
        security_notice=QPushButton(('🔔  هشدارهای امنیتی خوانده‌نشده: ' if self.language=='fa' else '🔔  Unread security alerts: ')+str(pending_alerts))
        security_notice.setObjectName('navButton')
        security_notice.clicked.connect(lambda:self.navigate(15))
        v.addWidget(security_notice)
       except (PermissionError,ValueError,sqlite3.Error,AttributeError):
        pass
      # Occupancy is scoped to the selected branch and today's actual stays.
      occupancy_row=QHBoxLayout()
      occupancy_title=QLabel('پیشرفت اشغال امروز' if self.language=='fa' else 'Today’s occupancy')
      occupancy_row.addWidget(occupancy_title)
      occupancy_bar=QProgressBar();occupancy_bar.setRange(0,100)
      occupancy_bar.setValue(round(kpis['occupancy_percent']))
      occupancy_bar.setFormat(f"{kpis['occupancy_percent']:.1f}%")
      occupancy_bar.setAccessibleName(occupancy_title.text())
      occupancy_bar.setStyleSheet('QProgressBar {background:#182e47;border:1px solid #33506c;border-radius:9px;min-height:21px;text-align:center;color:white;} QProgressBar::chunk {background:#14b8a6;border-radius:8px;}')
      occupancy_row.addWidget(occupancy_bar,1);v.addLayout(occupancy_row)
      period_row=QHBoxLayout()
      period_label=QLabel('گزارش دریافتی' if self.language=='fa' else 'Payment reporting window')
      period_row.addWidget(period_label)
      period_select=QComboBox()
      for days in (7,30,90):
       period_select.addItem(f'{days} روز گذشته' if self.language=='fa' else f'Last {days} days',days)
      period_row.addWidget(period_select)
      period_result=QLabel();period_result.setWordWrap(True);period_result.setObjectName('subtitle')
      period_row.addWidget(period_result,1)
      def update_period():
       days=period_select.currentData()
       begin,finish=reporting_window(today,days)
       # The previous period has the same number of calendar days.
       previous_end=(date.fromisoformat(begin)-timedelta(days=1)).isoformat()
       previous_begin,_=reporting_window(previous_end,days)
       with connect() as report_db:
        current=payment_totals(report_db,self.active_branch,begin,finish)
        previous=payment_totals(report_db,self.active_branch,previous_begin,previous_end)
       change=compare_periods(current['revenue'],previous['revenue'])
       delta=('—' if change is None else f'{change:+.1f}%')
       if self.language=='fa':
        period_result.setText(f"{self.format_date(begin)} تا {self.format_date(finish)} | {current['payments']} پرداخت | {self.format_money(current['revenue'])} | تغییر: {delta}")
       else:
        period_result.setText(f"{begin} to {finish} | {current['payments']} payments | {self.format_money(current['revenue'])} | Change: {delta}")
      period_select.currentIndexChanged.connect(lambda _index:update_period())
      v.addLayout(period_row);update_period()
      from dashboard_insights import occupancy_message, revenue_change, revenue_message
      insight=QLabel(occupancy_message(kpis['occupancy_percent'],self.language))
      insight.setObjectName('subtitle');insight.setWordWrap(True);v.addWidget(insight)
      quick_panel=QWidget();quick=QGridLayout(quick_panel)
      quick.setContentsMargins(0,0,0,0);quick.setHorizontalSpacing(10);quick.setVerticalSpacing(10)
      quick_actions=[
       ('＋ رزرو جدید' if self.language=='fa' else '+ New booking',2),
       ('نمایش نقشه اشغال' if self.language=='fa' else 'Occupancy map',20),
       ('مدیریت پرداخت‌ها' if self.language=='fa' else 'Manage payments',4),
       ('گزارش شعبه' if self.language=='fa' else 'Branch report',24)]
      for idx,(label,target) in enumerate(quick_actions):
       action=QPushButton(label);action.setObjectName('primary' if target==2 else 'quickAction')
       action.setMinimumHeight(42)
       action.clicked.connect(lambda checked=False,index=target:self.navigate(index))
       quick.addWidget(action,idx//2,idx%2)
      quick.setColumnStretch(0,1);quick.setColumnStretch(1,1)
      v.addWidget(quick_panel)
      # v89: standalone, branch-authorized indicative accommodation dashboard.
      def open_accommodation_dashboard():
       from revenue_occupancy_dashboard import report_window, dashboard_kpis, dashboard_alerts
       fa=self.language=='fa'
       dialog=QDialog(self);dialog.setWindowTitle('داشبورد درآمد و اشغال' if fa else 'Revenue & Occupancy Dashboard')
       dialog.resize(1120,820)
       dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
       outer=QVBoxLayout(dialog)
       scroll=QScrollArea(dialog);scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.Shape.NoFrame)
       content=QWidget();layout=QVBoxLayout(content);layout.setSpacing(12)
       scroll.setWidget(content);outer.addWidget(scroll)
       heading=QLabel('شاخص‌های تخمینی اقامت • شعبه فعال' if fa else 'Indicative accommodation metrics • Active branch')
       heading.setObjectName('subtitle');layout.addWidget(heading)
       period=QComboBox()
       for days in (7,30,90):period.addItem(f'{days} روز گذشته' if fa else f'Last {days} days',days)
       layout.addWidget(period)
       metrics=QLabel();metrics.setWordWrap(True);metrics.setObjectName('subtitle');layout.addWidget(metrics)
       progress=QProgressBar();progress.setRange(0,100);layout.addWidget(progress)
       alerts=QLabel();alerts.setWordWrap(True);layout.addWidget(alerts)
       # v90: period-over-period comparison and daily occupancy trend.
       trend_title=QLabel('مقایسه با دوره قبل و روند روزانه اشغال' if fa else 'Previous period comparison and daily occupancy trend')
       trend_title.setObjectName('subtitle');layout.addWidget(trend_title)
       comparison=QLabel();comparison.setWordWrap(True);layout.addWidget(comparison)
       from occupancy_trend_chart import OccupancyTrendChart
       occupancy_chart=OccupancyTrendChart(self.language)
       layout.addWidget(occupancy_chart)
       trend_table=QTableWidget();trend_table.setColumnCount(3)
       trend_table.setHorizontalHeaderLabels(['تاریخ','اتاق اشغال','درصد اشغال'] if fa else ['Date','Occupied rooms','Occupancy %'])
       trend_table.setMaximumHeight(180);layout.addWidget(trend_table)
       # v91: branch-authorized breakdown of accommodation estimates by room type.
       room_type_title=QLabel('تحلیل اقامت به تفکیک نوع اتاق' if fa else 'Accommodation by room type')
       room_type_title.setObjectName('subtitle');layout.addWidget(room_type_title)
       room_type_table=QTableWidget();room_type_table.setColumnCount(7)
       room_type_table.setHorizontalHeaderLabels(
        ['نوع اتاق','اشغال ٪','شب‌اتاق','ارزش تخمینی','ADR','RevPAR','بدون نرخ'] if fa
        else ['Room type','Occupancy %','Room-nights','Estimated value','ADR','RevPAR','Missing quotes'])
       room_type_table.setMaximumHeight(170);layout.addWidget(room_type_table)
       # v92: equal-duration comparisons of room types.
       type_comparison_title=QLabel('مقایسه انواع اتاق با دوره قبل' if fa else 'Room types vs previous period')
       type_comparison_title.setObjectName('subtitle');layout.addWidget(type_comparison_title)
       type_comparison_table=QTableWidget();type_comparison_table.setColumnCount(7)
       type_comparison_table.setHorizontalHeaderLabels(
        ['نوع اتاق','اشغال فعلی','تغییر اشغال (واحد درصد)','ADR فعلی','تغییر ADR','RevPAR فعلی','تغییر RevPAR'] if fa
        else ['Room type','Current occupancy','Occupancy change (pp)','Current ADR','ADR change','Current RevPAR','RevPAR change'])
       type_comparison_table.setMaximumHeight(225)
       type_comparison_table.setAlternatingRowColors(True)
       type_comparison_table.setSortingEnabled(False)
       type_comparison_table.horizontalHeader().setStretchLastSection(True)
       layout.addWidget(type_comparison_table)
       # v94: configurable, local-only room-type performance review.
       ranking_controls=QHBoxLayout()
       ranking_label=QLabel('رتبه‌بندی بر اساس' if fa else 'Rank room types by')
       ranking_metric=QComboBox()
       for caption,key in (
        (('RevPAR تخمینی' if fa else 'Indicative RevPAR'),'estimated_revpar'),
        (('ADR تخمینی' if fa else 'Indicative ADR'),'estimated_adr'),
        (('نرخ اشغال' if fa else 'Occupancy'),'occupancy_percent'),
        (('ارزش تخمینی' if fa else 'Estimated value'),'estimated_value')):
        ranking_metric.addItem(caption,key)
       ranking_controls.addWidget(ranking_label);ranking_controls.addWidget(ranking_metric)
       ranking_controls.addStretch(1)
       ranking_export=QPushButton('CSV رتبه‌بندی' if fa else 'Export ranking CSV')
       ranking_controls.addWidget(ranking_export)
       layout.addLayout(ranking_controls)
       ranking_table=QTableWidget();ranking_table.setColumnCount(4)
       ranking_table.setHorizontalHeaderLabels(
        ['رتبه','نوع اتاق','شاخص انتخابی','وضعیت نرخ'] if fa
        else ['Rank','Room type','Selected metric','Rate status'])
       ranking_table.setAlternatingRowColors(True)
       ranking_table.setMaximumHeight(200)
       layout.addWidget(ranking_table)
       alert_controls=QHBoxLayout()
       alert_controls.addWidget(QLabel('هشدار اشغال زیر ٪' if fa else 'Alert occupancy below %'))
       from executive_room_report import validate_thresholds
       preferences=QSettings('AshkanHotelPro','RevenueAlerts')
       preference_prefix=f'account_{self.user_id}/branch_{self.active_branch}'
       low_occ=QSpinBox();low_occ.setRange(0,100)
       try: saved_low=int(preferences.value(preference_prefix+'/low_occupancy',40))
       except (TypeError,ValueError): saved_low=40
       low_occ.setValue(min(100,max(0,saved_low)));alert_controls.addWidget(low_occ)
       alert_controls.addWidget(QLabel('هشدار رزرو بدون نرخ بیش از' if fa else 'Alert missing quotes above'))
       missing_limit=QSpinBox();missing_limit.setRange(0,10000)
       try: saved_missing=int(preferences.value(preference_prefix+'/missing_quotes',0))
       except (TypeError,ValueError): saved_missing=0
       missing_limit.setValue(min(10000,max(0,saved_missing)));alert_controls.addWidget(missing_limit)
       def save_alert_preferences():
        try:
         low,missing=validate_thresholds(low_occ.value(),missing_limit.value())
         preferences.setValue(preference_prefix+'/low_occupancy',low)
         preferences.setValue(preference_prefix+'/missing_quotes',missing)
         preferences.sync()
        except ValueError as exc: QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       save_alert_button=QPushButton('ذخیره آستانه‌های هشدار' if fa else 'Save alert thresholds')
       save_alert_button.clicked.connect(save_alert_preferences)
       alert_controls.addWidget(save_alert_button)
       layout.addLayout(alert_controls)
       custom_alerts=QLabel();custom_alerts.setWordWrap(True);layout.addWidget(custom_alerts)
       room_type_warnings=QLabel();room_type_warnings.setWordWrap(True);layout.addWidget(room_type_warnings)
       warning=QLabel('تخمینی، نه درآمد تحقق‌یافته؛ بر اساس نرخ رزرو و موجودی فعلی اتاق‌ها.' if fa else 'Indicative, not recognized revenue; based on booking quotes and current room inventory.')
       warning.setWordWrap(True);layout.addWidget(warning)
       export_button=QPushButton('خروجی Excel' if fa else 'Export Excel');layout.addWidget(export_button)
       # v96: interactive multi-property executive overview, admin only.
       if self.role=='admin':
        multi_property_button=QPushButton('داشبورد مرکزی شعب' if fa else 'Multi-property executive dashboard')
        layout.addWidget(multi_property_button)
        def open_multi_property():
         from multi_property_dashboard import branch_scorecard,overview_totals
         panel=QDialog(dialog)
         panel.setWindowTitle('داشبورد مرکزی شعب' if fa else 'Multi-property dashboard')
         panel.resize(1040,660)
         panel.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
         outer_layout=QVBoxLayout(panel)
         scroll_panel=QScrollArea(panel);scroll_panel.setWidgetResizable(True)
         scroll_panel.setFrameShape(QFrame.Shape.NoFrame)
         scroll_content=QWidget();content=QVBoxLayout(scroll_content)
         scroll_panel.setWidget(scroll_content);outer_layout.addWidget(scroll_panel)
         heading=QLabel('مقایسه عملکرد شعب مجاز' if fa else 'Authorized property performance')
         content.addWidget(heading)
         summary=QLabel();summary.setWordWrap(True);content.addWidget(summary)
         table=QTableWidget();table.setColumnCount(7)
         table.setHorizontalHeaderLabels(['شعبه','اتاق فعال','اشغال','ADR تخمینی','RevPAR تخمینی','رزرو بدون نرخ','هشدارها'] if fa else ['Property','Active rooms','Occupancy','Indicative ADR','Indicative RevPAR','Missing quotes','Alerts'])
         table.setAlternatingRowColors(True);table.horizontalHeader().setStretchLastSection(True)
         content.addWidget(table)
         # v99: executive KPI tiles and comparative ADR/RevPAR bars.
         from property_executive_visuals import kpi_display,comparative_bars
         kpi_grid=QGridLayout()
         kpi_tiles=[]
         for tile_index in range(6):
          tile=QFrame();tile.setObjectName('executiveKpiTile')
          tile.setStyleSheet('QFrame#executiveKpiTile { background: #123047; border: 1px solid #25495f; border-radius: 12px; padding: 10px; } QLabel { color: #f8fafc; }')
          tile_layout=QVBoxLayout(tile)
          caption=QLabel();caption.setStyleSheet('color:#9dd7d0; font-size:12px;')
          amount=QLabel();amount.setStyleSheet('font-size:19px; font-weight:700;')
          tile_layout.addWidget(caption);tile_layout.addWidget(amount)
          kpi_grid.addWidget(tile,tile_index//3,tile_index%3)
          kpi_tiles.append((caption,amount))
         content.insertLayout(2,kpi_grid)
         comparison_heading=QLabel('مقایسه ADR و RevPAR شعب' if fa else 'Property ADR / RevPAR comparison')
         content.addWidget(comparison_heading)
         comparison_metric=QComboBox()
         comparison_metric.addItem('ADR','estimated_adr')
         comparison_metric.addItem('RevPAR','estimated_revpar')
         content.addWidget(comparison_metric)
         comparison_bars_widget=QWidget()
         comparison_bars_layout=QVBoxLayout(comparison_bars_widget)
         content.addWidget(comparison_bars_widget)
         from property_insights import filtered_rankings, chart_bars
         controls=QHBoxLayout()
         branch_filter=QLineEdit();branch_filter.setPlaceholderText('جستجوی شعبه' if fa else 'Search property')
         metric_filter=QComboBox()
         for caption,key in [('اشغال' if fa else 'Occupancy','occupancy_percent'),('ADR','estimated_adr'),('RevPAR','estimated_revpar'),('ارزش تخمینی' if fa else 'Estimated value','estimated_value')]:metric_filter.addItem(caption,key)
         alert_filter=QCheckBox('فقط شعب هشدار‌دار' if fa else 'Alerts only')
         controls.addWidget(branch_filter);controls.addWidget(metric_filter);controls.addWidget(alert_filter)
         content.insertLayout(2,controls)
         chart_box=QWidget();chart_layout=QVBoxLayout(chart_box)
         content.addWidget(chart_box)
         compare_button=QPushButton('مقایسه با دوره قبل' if fa else 'Compare with previous period')
         content.addWidget(compare_button)
         period_comparison=QLabel();period_comparison.setWordWrap(True)
         content.addWidget(period_comparison)
         pdf_button=QPushButton('خروجی PDF مدیریتی' if fa else 'Export executive PDF');content.addWidget(pdf_button)
         note=QLabel('برآورد بر اساس نرخ رزرو و موجودی فعلی؛ درآمد تحقق‌یافته نیست.' if fa else 'Indicative booking-quote values and current room inventory; not recognized revenue.')
         note.setWordWrap(True);content.addWidget(note)
         try:
          start,end=report_window(date.today().isoformat(),period.currentData())
          with connect() as db:
           rows=branch_scorecard(db,user_id=self.user_id,role=self.role,start=start,end=end,low_occupancy=low_occ.value())
          totals=overview_totals(rows)
          for (caption,value),(title,number) in zip(kpi_tiles,kpi_display(totals,self.language)):
           caption.setText(title);value.setText(number)
          occ='—' if totals['occupancy_percent'] is None else f"{totals['occupancy_percent']:.1f}%"
          summary.setText((f"شعب: {totals['branches']} | اتاق‌ها: {totals['rooms']} | اشغال کل: {occ} | رزروهای بدون نرخ: {totals['missing_quotes']}" if fa else f"Properties: {totals['branches']} | Rooms: {totals['rooms']} | Weighted occupancy: {occ} | Missing quotes: {totals['missing_quotes']}"))
          def redraw_comparison():
           while comparison_bars_layout.count():
            child=comparison_bars_layout.takeAt(0)
            if child.widget():child.widget().deleteLater()
           visible=filtered_rankings(rows,search=branch_filter.text(),metric=comparison_metric.currentData(),only_alerts=alert_filter.isChecked())
           for item in comparative_bars(visible,comparison_metric.currentData()):
            wrapper=QWidget();line=QHBoxLayout(wrapper)
            name=QLabel(item['branch_name']);name.setMinimumWidth(140)
            progress=QProgressBar();progress.setRange(0,100);progress.setValue(item['percent']);progress.setFormat('')
            progress.setStyleSheet('QProgressBar {background:#e2e8f0; border:0; border-radius:5px; height:14px;} QProgressBar::chunk {background:#0d9488; border-radius:5px;}')
            amount=QLabel(f"{item['value']:,.2f}");amount.setMinimumWidth(90)
            line.addWidget(name);line.addWidget(progress,1);line.addWidget(amount)
            comparison_bars_layout.addWidget(wrapper)
          def redraw():
           visible=filtered_rankings(rows,search=branch_filter.text(),metric=metric_filter.currentData(),only_alerts=alert_filter.isChecked())
           table.setRowCount(len(visible))
           for ri,item in enumerate(visible):
            def fmt(value,percent=False):
             return '—' if value is None else (f'{value:.1f}%' if percent else self.format_money(value))
            flags={'missing_quotes':('نرخ ناقص' if fa else 'Missing rates'),'overcapacity':('بیش از ظرفیت' if fa else 'Overcapacity'),'no_active_rooms':('بدون اتاق فعال' if fa else 'No active rooms'),'low_occupancy':('اشغال پایین' if fa else 'Low occupancy')}
            values=(item['branch_name'],item['rooms'],fmt(item['occupancy_percent'],True),fmt(item['estimated_adr']),fmt(item['estimated_revpar']),item['missing_quotes'],', '.join(flags[a] for a in item['alerts']) or '—')
            for ci,value in enumerate(values):table.setItem(ri,ci,QTableWidgetItem(str(value)))
           while chart_layout.count():
            child=chart_layout.takeAt(0)
            if child.widget():child.widget().deleteLater()
           for item in chart_bars(visible[:12],metric=metric_filter.currentData()):
            bar_row=QHBoxLayout();label=QLabel(str(item['branch_name']));label.setMinimumWidth(140)
            bar=QProgressBar();bar.setRange(0,100);bar.setValue(item['percent']);bar.setFormat('')
            bar_row.addWidget(label);bar_row.addWidget(bar)
            wrapper=QWidget();wrapper.setLayout(bar_row);chart_layout.addWidget(wrapper)
          comparison_metric.currentIndexChanged.connect(lambda _:redraw_comparison())
          branch_filter.textChanged.connect(lambda _:redraw_comparison())
          alert_filter.toggled.connect(lambda _:redraw_comparison())
          branch_filter.textChanged.connect(lambda _:redraw())
          metric_filter.currentIndexChanged.connect(lambda _:redraw())
          alert_filter.toggled.connect(lambda _:redraw())
          def export_pdf():
           path,_=QFileDialog.getSaveFileName(panel,'PDF','multi_property_report.pdf','PDF Files (*.pdf)')
           if path:
            try:
             from property_pdf import export_property_pdf
             export_property_pdf(path,filtered_rankings(rows,search=branch_filter.text(),metric=metric_filter.currentData(),only_alerts=alert_filter.isChecked()),start=start,end=end,language=self.language)
            except (ImportError,OSError,ValueError) as exc:QMessageBox.warning(panel,'خطا' if fa else 'Error',str(exc))
          def compare_previous():
           try:
            from property_period_comparison import compare_property_periods
            with connect() as db:
             comparison=compare_property_periods(db,user_id=self.user_id,role=self.role,start=start,end=end,low_occupancy=low_occ.value())
            lines=[]
            for item in comparison['rows']:
             change=item['changes']['occupancy_percent']
             change_text='—' if change is None else f'{change:+.1f} pp'
             lines.append(f"{item['branch_name']}: {change_text}")
            period_comparison.setText(('تغییر اشغال نسبت به دوره قبل: ' if fa else 'Occupancy change vs previous period: ')+' | '.join(lines))
           except (ValueError,PermissionError,TypeError) as exc:
            QMessageBox.warning(panel,'خطا' if fa else 'Error',str(exc))
          compare_button.clicked.connect(compare_previous)
          pdf_button.clicked.connect(export_pdf)
          redraw()
          redraw_comparison()
          table.resizeColumnsToContents()
         except (ValueError,PermissionError,TypeError) as exc:
          QMessageBox.warning(panel,'خطا' if fa else 'Error',str(exc));return
         panel.exec()
        multi_property_button.clicked.connect(open_multi_property)
       # Only administrators can compare multiple branches; all rows are authorized.
       if self.role=='admin':
        branch_compare_button=QPushButton('گزارش مقایسه شعب (CSV)' if fa else 'Compare branches (CSV)')
        layout.addWidget(branch_compare_button)
        def export_branches():
         from executive_room_report import branch_room_type_comparison,export_branch_comparison_csv
         try:
          start,end=report_window(date.today().isoformat(),period.currentData())
          with connect() as db:
           from branch_access import allowed_branches
           branch_ids=[branch_id for branch_id,_ in allowed_branches(db,self.user_id,self.role)]
           if not branch_ids:
            QMessageBox.information(dialog,'اطلاع' if fa else 'Info','شعبه فعالی وجود ندارد.' if fa else 'No active branches.')
            return
           rows=branch_room_type_comparison(db,branch_ids=branch_ids,start=start,end=end,user_id=self.user_id,role=self.role)
          path,_=QFileDialog.getSaveFileName(dialog,'CSV','branch_room_type_comparison.csv','CSV Files (*.csv)')
          if path:export_branch_comparison_csv(path,rows)
         except (OSError,ValueError,PermissionError) as exc:
          QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
        branch_compare_button.clicked.connect(export_branches)
       cached_types=[]
       def refresh_room_ranking():
        from room_type_management import ranked_room_types,room_type_risks
        metric=ranking_metric.currentData()
        ranked=ranked_room_types(cached_types,metric)
        ranking_table.setRowCount(len(ranked))
        for index,item in enumerate(ranked):
         value=item.get(metric)
         label='—' if value is None else (f'{value:,.1f}%' if metric=='occupancy_percent' else self.format_money(value))
         values=(str(index+1),str(item.get('kind','')),label,
                 ('بدون نرخ' if fa else 'Missing rates') if item.get('missing_quotes',0) else ('کامل' if fa else 'Complete'))
         for column,value in enumerate(values):
          ranking_table.setItem(index,column,QTableWidgetItem(str(value)))
        warnings=room_type_risks(cached_types,low_occupancy=low_occ.value(),high_missing_quotes=missing_limit.value())
        if warnings:
         custom_alerts.setText('\n'.join(
          (f'{kind}: اشغال پایین ({value}٪)' if code=='low_occupancy' else f'{kind}: {value} رزرو بدون نرخ') if fa
          else (f'{kind}: low occupancy ({value}%)' if code=='low_occupancy' else f'{kind}: {value} missing quotes')
          for kind,code,value in warnings))
        else:custom_alerts.setText('هشداری با آستانه‌های انتخابی وجود ندارد.' if fa else 'No warnings for selected thresholds.')
       def export_room_ranking():
        from room_type_management import export_room_type_ranking_csv
        path,_=QFileDialog.getSaveFileName(dialog,'CSV','room_type_ranking.csv','CSV Files (*.csv)')
        if path:
         try:export_room_type_ranking_csv(path,cached_types,metric=ranking_metric.currentData())
         except (OSError,ValueError) as exc:QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       ranking_metric.currentIndexChanged.connect(lambda _index:refresh_room_ranking())
       low_occ.valueChanged.connect(lambda _value:refresh_room_ranking())
       missing_limit.valueChanged.connect(lambda _value:refresh_room_ranking())
       ranking_export.clicked.connect(export_room_ranking)
       def load_dashboard():
        start,end=report_window(date.today().isoformat(),period.currentData())
        with connect() as db:
         perf=estimated_branch_performance(db,branch_id=self.active_branch,start=start,end=end,user_id=self.user_id,role=self.role)
        kpi=dashboard_kpis(perf)
        occ='—' if kpi['occupancy_percent'] is None else f"{kpi['occupancy_percent']:.1f}%"
        adr='—' if kpi['estimated_adr'] is None else self.format_money(kpi['estimated_adr'])
        revpar='—' if kpi['estimated_revpar'] is None else self.format_money(kpi['estimated_revpar'])
        if fa:metrics.setText(f"بازه: {self.format_date(start)} تا {self.format_date((date.fromisoformat(end)-timedelta(days=1)).isoformat())}\nاشغال: {occ}  |  ADR تخمینی: {adr}  |  RevPAR تخمینی: {revpar}\nارزش تخمینی اقامت: {self.format_money(kpi['estimated_value'])}")
        else:metrics.setText(f"Period: {start} to {(date.fromisoformat(end)-timedelta(days=1)).isoformat()}\nOccupancy: {occ}  |  Indicative ADR: {adr}  |  Indicative RevPAR: {revpar}\nEstimated stay value: {self.format_money(kpi['estimated_value'])}")
        progress.setValue(min(100,max(0,round(kpi['occupancy_percent'] or 0))))
        alerts.setText('\n'.join(dashboard_alerts(kpi,self.language)))
        from stay_trends import compare_periods, daily_occupancy
        with connect() as db:
         comparison_data=compare_periods(db,branch_id=self.active_branch,start=start,end=end,user_id=self.user_id,role=self.role)
         daily=daily_occupancy(db,branch_id=self.active_branch,start=start,end=end,user_id=self.user_id,role=self.role)
        from room_type_analytics import room_type_performance, room_type_alerts
        with connect() as db:
         by_type=room_type_performance(db,branch_id=self.active_branch,start=start,end=end,user_id=self.user_id,role=self.role)
        cached_types[:]=by_type
        refresh_room_ranking()
        room_type_table.setRowCount(len(by_type))
        for row_idx,item in enumerate(by_type):
         fields=(item['kind'],
                 '—' if item['occupancy_percent'] is None else f"{item['occupancy_percent']:.1f}%",
                 str(item['occupied_nights']),self.format_money(item['estimated_value']),
                 '—' if item['estimated_adr'] is None else self.format_money(item['estimated_adr']),
                 '—' if item['estimated_revpar'] is None else self.format_money(item['estimated_revpar']),
                 str(item['missing_quotes']))
         for col_idx,value in enumerate(fields):
          room_type_table.setItem(row_idx,col_idx,QTableWidgetItem(str(value)))
        room_type_warnings.setText('\n'.join(room_type_alerts(by_type,self.language)))
        from room_type_comparison import compare_room_types
        with connect() as db:
         type_comparison=compare_room_types(db,branch_id=self.active_branch,start=start,end=end,user_id=self.user_id,role=self.role)
        type_comparison_table.setRowCount(len(type_comparison['rows']))
        def show_delta(value,unit=''):
         return '—' if value is None else f'{value:+,.2f}{unit}'
        for ri,item in enumerate(type_comparison['rows']):
         fields=(item['kind'],
                 '—' if item['occupancy_now'] is None else f"{item['occupancy_now']:.1f}%",
                 show_delta(item['occupancy_delta_pp'],' pp'),
                 '—' if item['adr_now'] is None else self.format_money(item['adr_now']),
                 show_delta(item['adr_delta']),
                 '—' if item['revpar_now'] is None else self.format_money(item['revpar_now']),
                 show_delta(item['revpar_delta']))
         for ci,value in enumerate(fields):
          type_comparison_table.setItem(ri,ci,QTableWidgetItem(str(value)))

        change=comparison_data['changes']['occupancy_percent']
        change_text='—' if change is None else f'{change:+.1f} pp'
        comparison.setText((f'تغییر اشغال نسبت به دوره قبل: {change_text}' if fa else f'Occupancy change vs previous period: {change_text}') +
                           (' | داده‌های تخمینی' if fa else ' | indicative estimates'))
        occupancy_chart.set_series(daily)
        trend_table.setRowCount(len(daily))
        for row_idx,day in enumerate(daily):
         for col_idx,value in enumerate((day['date'],str(day['occupied']),
                                        '—' if day['occupancy_percent'] is None else f"{day['occupancy_percent']:.1f}%")):
          trend_table.setItem(row_idx,col_idx,QTableWidgetItem(value))

        return start,end,perf
       def export_dashboard():
        start,end,perf=load_dashboard()
        path,_=QFileDialog.getSaveFileName(dialog,'Excel','accommodation_dashboard.xlsx','Excel Files (*.xlsx)')
        if path:
         try:
          with connect() as db:
           branch=db.execute('SELECT name FROM branches WHERE id=?',(self.active_branch,)).fetchone()
          export_estimated_performance(path,[dict(perf,branch_name=branch[0] if branch else str(self.active_branch))],start=start,end=end,language=self.language)
         except (OSError,ValueError,ImportError) as exc:QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       period.currentIndexChanged.connect(lambda _index:load_dashboard())
       export_button.clicked.connect(export_dashboard)
       load_dashboard();dialog.exec()
      accommodation_button=QPushButton('داشبورد درآمد و اشغال' if self.language=='fa' else 'Revenue & Occupancy Dashboard')
      accommodation_button.clicked.connect(open_accommodation_dashboard)
      v.addWidget(accommodation_button)
      monthly=c.execute('SELECT substr(p.created_at,1,7),SUM(p.amount) FROM payments p JOIN reservations r ON r.id=p.reservation_id WHERE r.branch_id=? GROUP BY substr(p.created_at,1,7) ORDER BY 1 DESC LIMIT 6',(self.active_branch,)).fetchall()
      trend=list(reversed(monthly))
      change=revenue_change(trend)
      if change is not None:
       delta=QLabel(revenue_message(change,self.language));delta.setObjectName('subtitle');v.addWidget(delta)
      v.addWidget(QLabel('Monthly branch receipts' if self.language=='en' else 'روند دریافتی ماهانه شعبه'))
      v.addWidget(RevenueChart(trend,self.language))
      v.addWidget(QLabel('Recent branch reservations' if self.language=='en' else 'آخرین رزروهای شعبه'))
      recent=c.execute('SELECT r.id,ro.number,g.name,r.status FROM reservations r JOIN rooms ro ON ro.id=r.room_id JOIN guests g ON g.id=r.guest_id WHERE r.branch_id=? ORDER BY r.id DESC LIMIT 5',(self.active_branch,)).fetchall()
      v.addWidget(self.table(['ID','Room','Guest','Status'] if self.language=='en' else ['شناسه','اتاق','مهمان','وضعیت'],recent))
     elif i==1:
      w,v=self.page('مدیریت اتاق‌ها');rows=[(n,k,self.format_money(rate),status) for n,k,rate,status in c.execute('SELECT number,kind,rate,status FROM rooms WHERE branch_id=? ORDER BY number',(self.active_branch,))];v.addWidget(self.table(['شماره','نوع','نرخ هر شب','وضعیت'],rows));add=QPushButton('＋ افزودن اتاق');add.setObjectName('primary');add.clicked.connect(self.add_room);v.addWidget(add)
     elif i==2:
      w,v=self.page('رزروها');b=QPushButton('＋ رزرو جدید');b.setObjectName('primary');b.clicked.connect(self.add_booking);v.addWidget(b)
      audit_button=QPushButton('🕘 تاریخچه تغییرات رزرو' if self.language=='fa' else '🕘 Reservation audit history')
      audit_button.setToolTip('نمایش رویدادهای ثبت‌شده در تاریخچه رزروها' if self.language=='fa' else 'Browse recorded reservation change events')
      audit_button.setVisible(self.role=='admin')
      audit_button.clicked.connect(self.open_booking_audit)
      v.addWidget(audit_button)
      rows=[(rid,n,g,self.format_date(start),self.format_date(end),status) for rid,n,g,start,end,status in c.execute('SELECT r.id,ro.number,g.name,r.checkin,r.checkout,r.status FROM reservations r JOIN rooms ro ON ro.id=r.room_id JOIN guests g ON g.id=r.guest_id WHERE r.branch_id=? ORDER BY r.id DESC',(self.active_branch,))]
      filters=QHBoxLayout()
      search=QLineEdit();search.setClearButtonEnabled(True)
      search.setPlaceholderText('جست‌وجوی رزرو، اتاق یا مهمان...' if self.language=='fa' else 'Search booking, room or guest...')
      filters.addWidget(search,3)
      status_filter=QComboBox()
      for label,value in status_options(self.language):status_filter.addItem(label,value)
      filters.addWidget(status_filter,1);v.addLayout(filters)
      self.res_table=self.table([translate(h,self.language) for h in ('شناسه','اتاق','مهمان','ورود (شمسی)','خروج (شمسی)','وضعیت')],rows)
      self.res_table.setAlternatingRowColors(True)
      self.res_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
      self.res_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
      self.res_table.setMinimumHeight(310)
      for row_idx,entry in enumerate(rows):
       item=self.res_table.item(row_idx,5)
       if item:
        from PySide6.QtGui import QColor, QBrush
        foreground,background=status_color(entry[5])
        item.setForeground(QBrush(QColor(foreground)));item.setBackground(QBrush(QColor(background)))
        item.setText(translate(entry[5],self.language))
      v.addWidget(self.res_table)
      self.res_status_filter=status_filter
      search.textChanged.connect(lambda _:self.filter_reservations(search.text()))
      status_filter.currentIndexChanged.connect(lambda _:self.filter_reservations(search.text()))
      actions=QHBoxLayout()
      edit=QPushButton('تغییر اتاق یا تاریخ رزرو' if self.language=='fa' else 'Edit room or dates');edit.clicked.connect(self.edit_booking);actions.addWidget(edit)
      for title,status in [('پذیرش مهمان','پذیرش شده'),('تسویه و خروج','خارج شده'),('لغو رزرو','لغو شده')]:
       b=QPushButton(translate(title,self.language));b.clicked.connect(lambda _,s=status:self.change_status(s));actions.addWidget(b)
      v.addLayout(actions)
     elif i==3:
      w,v=self.page(translate('مهمانان',self.language))
      guest_rows=c.execute('SELECT DISTINCT g.name,g.phone,g.national_id FROM guests g JOIN reservations r ON r.guest_id=g.id WHERE r.branch_id=? ORDER BY g.name',(self.active_branch,)).fetchall()
      summary=QLabel(translate('تعداد مهمانان',self.language)+': '+str(len(guest_rows)))
      summary.setObjectName('metric');v.addWidget(summary)
      guest_table=self.table([translate(h,self.language) for h in ('نام','تلفن','کد ملی')],guest_rows)
      guest_table.setAccessibleName(translate('فهرست مهمانان',self.language))
      guest_search=QLineEdit();guest_search.setClearButtonEnabled(True)
      guest_search.setPlaceholderText('Search guests by name, phone or ID…' if self.language=='en' else 'جستجوی مهمان بر اساس نام، تلفن یا کد ملی…')
      guest_search.setAccessibleName('Guest search' if self.language=='en' else 'جستجوی مهمان')
      v.addWidget(guest_search);v.addWidget(guest_table)
      guest_search.textChanged.connect(lambda query,table=guest_table: filter_table_rows(table,query))
     elif i==4:
      w,v=self.page(translate('پرداخت‌ها',self.language));self.payment_res=QComboBox()
      for rid,name in c.execute('SELECT r.id,g.name FROM reservations r JOIN guests g ON g.id=r.guest_id WHERE r.branch_id=? ORDER BY r.id DESC',(self.active_branch,)):
       self.payment_res.addItem(f"{translate('رزرو',self.language)} {rid} - {name}",rid)
      self.amount=QSpinBox();self.amount.setRange(1,2000000000);self.amount.setSingleStep(100000)
      self.method=QComboBox()
      for method in ('کارتخوان','نقدی','انتقال بانکی'):
       self.method.addItem(translate(method,self.language),method)
      form=QFormLayout()
      form.addRow(translate('رزرو',self.language),self.payment_res)
      form.addRow(translate('مبلغ',self.language)+' (toman)',self.amount)
      form.addRow(translate('روش پرداخت',self.language),self.method)
      v.addLayout(form)
      self.payment_error=QLabel('');self.payment_error.setObjectName('fieldError')
      self.payment_error.setWordWrap(True);self.payment_error.hide();v.addWidget(self.payment_error)
      self.payment_res.currentIndexChanged.connect(lambda _=None:self._validate_payment_form())
      self.amount.valueChanged.connect(lambda _=None:self._validate_payment_form())
      self.method.currentIndexChanged.connect(lambda _=None:self._validate_payment_form())
      b=QPushButton(translate('ثبت دریافت',self.language));b.setObjectName('primary');b.clicked.connect(self.pay);v.addWidget(b)
      payments=c.execute('SELECT p.reservation_id,p.amount,p.method,p.created_at FROM payments p JOIN reservations r ON r.id=p.reservation_id WHERE r.branch_id=? ORDER BY p.id DESC',(self.active_branch,)).fetchall()
      v.addWidget(self.table([translate(h,self.language) for h in ('رزرو','مبلغ','روش','زمان')],[(rid,self.format_money(a),translate(m,self.language),t) for rid,a,m,t in payments]))
     elif i==5:
      w,v=self.page('مدیریت خانه‌داری');rooms=c.execute('SELECT id,number FROM rooms WHERE branch_id=? ORDER BY number',(self.active_branch,)).fetchall();self.house_room=QComboBox()
      for rid,num in rooms:self.house_room.addItem('اتاق '+num,rid)
      self.house_task=QComboBox();self.house_task.addItems(['نظافت روزانه','نظافت پس از خروج','بازرسی','تعمیر و نگهداری'])
      h=QHBoxLayout();h.addWidget(self.house_room);h.addWidget(self.house_task);b=QPushButton('ثبت وظیفه');b.setObjectName('primary');b.clicked.connect(self.add_housekeeping);h.addWidget(b);v.addLayout(h)
      rows=c.execute('SELECT h.id,r.number,h.task,h.status,h.created_at FROM housekeeping h JOIN rooms r ON r.id=h.room_id WHERE r.branch_id=? ORDER BY h.id DESC',(self.active_branch,)).fetchall()
      self.house_table=self.table(['شناسه','اتاق','وظیفه','وضعیت','زمان'],rows);v.addWidget(self.house_table)
      done=QPushButton('✓ تکمیل وظیفه انتخاب‌شده');done.clicked.connect(self.finish_housekeeping);v.addWidget(done)
     elif i==6:
      w,v=self.page('گزارش‌های مدیریتی');total=c.execute('SELECT COUNT(*) FROM reservations WHERE branch_id=?',(self.active_branch,)).fetchone()[0];cancelled=c.execute("SELECT COUNT(*) FROM reservations WHERE branch_id=? AND status='لغو شده'",(self.active_branch,)).fetchone()[0]
      paid=c.execute('SELECT COALESCE(SUM(p.amount),0) FROM payments p JOIN reservations r ON r.id=p.reservation_id WHERE r.branch_id=?',(self.active_branch,)).fetchone()[0];rooms=c.execute("SELECT COUNT(*) FROM rooms WHERE status='فعال' AND branch_id=?",(self.active_branch,)).fetchone()[0]
      for k,val in [('تعداد کل رزروها',total),('رزروهای لغوشده',cancelled),('کل دریافتی',self.format_money(paid)),('اتاق‌های فعال',rooms)]:x=QLabel(f'{k}: {val}');x.setObjectName('metric');v.addWidget(x)
      v.addStretch()
     elif i==7:
      w,v=self.page('تنظیمات و پشتیبان‌گیری');v.addWidget(QLabel('پایگاه داده محلی SQLite — پیش از انتقال نسخه پشتیبان تهیه کنید.'))
      b=QPushButton('ذخیره نسخه پشتیبان پایگاه داده');b.setObjectName('primary');b.clicked.connect(self.backup);v.addWidget(b)
      b2=QPushButton('تغییر رمز عبور حساب فعلی');b2.clicked.connect(self.change_password);v.addWidget(b2);v.addStretch()
     elif i==8:
      w,v=self.page('مدیریت هزینه‌های هتل');self.exp_category=QComboBox();self.exp_category.addItems(['حقوق و دستمزد','تعمیرات','مواد مصرفی','آب و برق و گاز','بازاریابی','سایر'])
      self.exp_description=QLineEdit();self.exp_description.setPlaceholderText('شرح هزینه');self.exp_amount=QSpinBox();self.exp_amount.setMaximum(2000000000);self.exp_amount.setSingleStep(100000)
      for x in (self.exp_category,self.exp_description,self.exp_amount):v.addWidget(x)
      b=QPushButton('ثبت هزینه');b.setObjectName('primary');b.clicked.connect(self.add_expense);v.addWidget(b)
      rows=[(eid,cat,desc,self.format_money(amount),created) for eid,cat,desc,amount,created in c.execute('SELECT id,category,description,amount,created_at FROM expenses ORDER BY id DESC')]
      v.addWidget(self.table(['شناسه','دسته','شرح','مبلغ','تاریخ ثبت'],rows))
     elif i==9:
      w,v=self.page('مدیریت کارکنان');self.staff_name=QLineEdit();self.staff_name.setPlaceholderText('نام و نام خانوادگی');self.staff_position=QComboBox();self.staff_position.addItems(['پذیرش','خانه‌داری','مدیریت','حسابداری','نگهداری','رستوران'])
      self.staff_phone=QLineEdit();self.staff_phone.setPlaceholderText('شماره تماس');self.staff_salary=QSpinBox();self.staff_salary.setMaximum(2000000000);self.staff_salary.setSingleStep(1000000)
      for x in (self.staff_name,self.staff_position,self.staff_phone,self.staff_salary):v.addWidget(x)
      b=QPushButton('ثبت کارمند');b.setObjectName('primary');b.clicked.connect(self.add_employee);v.addWidget(b)
      rows=[(eid,name,pos,phone,self.format_money(salary),'فعال' if active else 'غیرفعال') for eid,name,pos,phone,salary,active in c.execute('SELECT id,full_name,position,phone,salary,active FROM employees ORDER BY id DESC')]
      self.staff_table=self.table(['شناسه','نام','سمت','تلفن','حقوق','وضعیت'],rows);v.addWidget(self.staff_table)
      b=QPushButton('تغییر وضعیت کارمند انتخاب‌شده');b.clicked.connect(self.toggle_employee);v.addWidget(b)
     elif i==10:
      w,v=self.page('صورتحساب رزروها');self.invoice_res=QComboBox()
      for rid,name,room in c.execute('SELECT r.id,g.name,ro.number FROM reservations r JOIN guests g ON g.id=r.guest_id JOIN rooms ro ON ro.id=r.room_id ORDER BY r.id DESC'):self.invoice_res.addItem(f'رزرو {rid} - {name} - اتاق {room}',rid)
      v.addWidget(self.invoice_res);b=QPushButton('نمایش صورتحساب');b.setObjectName('primary');b.clicked.connect(self.show_invoice);v.addWidget(b);pdfbtn=QPushButton('ذخیره PDF' if self.language=='fa' else 'Save PDF');pdfbtn.clicked.connect(self.export_invoice_pdf);v.addWidget(pdfbtn)
      b2=QPushButton('خروجی CSV رزروها');b2.clicked.connect(self.export_reservations);v.addWidget(b2);v.addStretch()
     elif i==11:
      w,v=self.page('تقویم اشغال و رزرو اتاق‌ها');cal=QCalendarWidget();cal.setGridVisible(True);v.addWidget(cal)
      details=QLabel();details.setWordWrap(True);v.addWidget(details)
      def refresh_calendar(qdate):
       day=qdate.toString('yyyy-MM-dd')
       with connect() as calendar_db:entries=calendar_db.execute("SELECT ro.number,g.name,r.status FROM reservations r JOIN rooms ro ON ro.id=r.room_id JOIN guests g ON g.id=r.guest_id WHERE r.checkin<=? AND r.checkout>? AND r.status IN ('رزرو شده','پذیرش شده') ORDER BY ro.number",(day,day)).fetchall()
       details.setText('تاریخ: '+self.format_date(day)+' | اتاق‌های رزروشده: '+str(len(entries))+'\n'+'\n'.join(f'اتاق {num} | {name} | {status}' for num,name,status in entries))
      cal.selectionChanged.connect(lambda:refresh_calendar(cal.selectedDate()));refresh_calendar(cal.selectedDate())
     elif i==12:
      w,v=self.page('رستوران و خدمات اقامت');self.order_res=QComboBox();self.order_item=QComboBox();self.order_qty=QSpinBox();self.order_qty.setRange(1,100)
      for rid,name in c.execute("SELECT r.id,g.name FROM reservations r JOIN guests g ON g.id=r.guest_id WHERE r.status IN ('رزرو شده','پذیرش شده') ORDER BY r.id DESC"):self.order_res.addItem(f'{rid} - {name}',rid)
      for mid,name,price in c.execute('SELECT id,name,price FROM menu_items WHERE active=1'):self.order_item.addItem(f'{name} | {self.format_money(price)}',mid)
      for title,widget in [('رزرو',self.order_res),('خدمت یا غذا',self.order_item),('تعداد',self.order_qty)]:v.addWidget(QLabel(title));v.addWidget(widget)
      b=QPushButton('ثبت سفارش و افزودن به صورتحساب');b.setObjectName('primary');b.clicked.connect(self.add_order);v.addWidget(b)
      rows=[(oid,guest,item,qty,self.format_money(qty*price),created) for oid,guest,item,qty,price,created in c.execute('SELECT o.id,g.name,m.name,o.quantity,o.unit_price,o.created_at FROM service_orders o JOIN reservations r ON r.id=o.reservation_id JOIN guests g ON g.id=r.guest_id JOIN menu_items m ON m.id=o.item_id ORDER BY o.id DESC LIMIT 150')]
      v.addWidget(self.table(['شماره','مهمان','خدمت','تعداد','مبلغ','زمان'],rows))
     elif i==13:
      w,v=self.page('مدیریت موجودی و هشدار کمبود');self.inv_name=QLineEdit();self.inv_name.setPlaceholderText('نام کالا');self.inv_unit=QComboBox();self.inv_unit.addItems(['عدد','کیلوگرم','لیتر','بسته']);self.inv_qty=QSpinBox();self.inv_qty.setMaximum(10000000);self.inv_min=QSpinBox();self.inv_min.setMaximum(10000000)
      for label,widget in [('نام کالا',self.inv_name),('واحد',self.inv_unit),('موجودی اولیه / مقدار افزایش',self.inv_qty),('حداقل موجودی',self.inv_min)]:v.addWidget(QLabel(label));v.addWidget(widget)
      b=QPushButton('ثبت کالا / افزایش موجودی');b.setObjectName('primary');b.clicked.connect(self.add_inventory);v.addWidget(b)
      rows=[(name,unit,qty,minimum,'⚠ کمبود' if qty<=minimum else 'مناسب') for name,unit,qty,minimum in c.execute('SELECT name,unit,quantity,minimum FROM inventory ORDER BY name')]
      v.addWidget(self.table(['کالا','واحد','موجودی','حداقل','وضعیت'],rows))
     elif i==14:
      w,v=self.page('تحلیل مالی و عملکرد');income=c.execute('SELECT COALESCE(SUM(amount),0) FROM payments').fetchone()[0];cost=c.execute('SELECT COALESCE(SUM(amount),0) FROM expenses').fetchone()[0];services=c.execute('SELECT COALESCE(SUM(quantity*unit_price),0) FROM service_orders').fetchone()[0]
      for label,value in [('دریافتی ثبت‌شده',self.format_money(income)),('هزینه‌های ثبت‌شده',self.format_money(cost)),('خدمات سفارش‌داده‌شده (نه لزوماً وصول‌شده)',self.format_money(services)),('خالص جریان نقدی ساده (دریافتی منهای هزینه)',self.format_money(income-cost))]:x=QLabel(label+'\n'+value);x.setObjectName('metric');v.addWidget(x)
      v.addStretch()
     elif i==15:
      from user_access_management import list_accounts,set_account_active,set_account_role,reset_account_password
      fa=self.language=='fa'
      w,v=self.page('مدیریت کاربران و نقش‌ها' if fa else 'User & Role Management')
      from security_overview import security_summary,recent_security_changes
      summary=security_summary(c,self.user_id)
      cards=QGridLayout()
      metrics=[
       ('ورود موفق' if fa else 'Successful logins',summary['success'],'#0F766E'),
       ('ورود ناموفق' if fa else 'Failed logins',summary['failure'],'#B45309'),
       ('حساب قفل‌شده' if fa else 'Locked attempts',summary['locked'],'#B91C1C'),
       ('نشست فعال' if fa else 'Active sessions',summary['active_sessions'],'#1D4ED8'),
       ('حساب غیرفعال' if fa else 'Disabled accounts',summary['disabled_accounts'],'#475569'),
       ('کل کاربران' if fa else 'Total accounts',summary['total_accounts'],'#0F766E')]
      for index,(label,value,accent) in enumerate(metrics):
       card=QFrame();card.setObjectName('securityMetricCard')
       card.setStyleSheet('QFrame#securityMetricCard{background:#152D40;border:1px solid #345064;border-radius:12px;padding:8px;}')
       card_layout=QVBoxLayout(card)
       title=QLabel(label);title.setStyleSheet('color:#D7E8EE;font-weight:600;')
       number=QLabel(str(value));number.setStyleSheet('color:#5EEAD4;font-size:26px;font-weight:800;')
       card_layout.addWidget(title);card_layout.addWidget(number)
       cards.addWidget(card,index//3,index%3)
      v.addLayout(cards)
      health_btn=QPushButton('◉  سلامت سیستم' if fa else '◉  System health')
      health_btn.setObjectName('primary')
      def show_system_health():
       from system_health_v119 import snapshot,history
       from operation_guard import authorize_action
       health_dialog=QDialog(self)
       health_dialog.setWindowTitle('سلامت سیستم' if fa else 'System Health')
       health_dialog.resize(1050,780)
       health_dialog.setMinimumSize(760,540)
       health_dialog.setStyleSheet("""
        QDialog {background:#0B1928;color:#E5F1F5;}
        QLabel {color:#D9EAF0;}
        QTableWidget {background:#10283A;alternate-background-color:#173347;
          color:#E5F1F5;gridline-color:#345166;border:1px solid #345166;border-radius:9px;}
        QHeaderView::section {background:#183B50;color:#E5F1F5;padding:7px;border:0;}
        QPushButton {background:#164B5C;color:#E9FAFA;border:1px solid #327587;
          border-radius:8px;padding:8px 12px;min-height:25px;}
        QPushButton:hover {background:#196579;}
        QSpinBox {background:#143348;color:#E5F1F5;padding:7px;border-radius:7px;}
       """)
       from PySide6.QtWidgets import QScrollArea, QGridLayout
       scroll=QScrollArea(health_dialog)
       scroll.setWidgetResizable(True)
       scroll.setFrameShape(QFrame.Shape.NoFrame)
       root_layout=QVBoxLayout(health_dialog)
       root_layout.addWidget(scroll)
       content=QWidget()
       scroll.setWidget(content)
       health_layout=QVBoxLayout(content)
       health_layout.setSpacing(12)
       heading=QLabel('داشبورد سلامت سیستم' if fa else 'System Health Dashboard')
       heading.setStyleSheet('font-size:23px;font-weight:800;color:#F0FBFF;')
       health_layout.addWidget(heading)
       subtitle=QLabel('نمای کلی، روند روزانه و مقایسه دوره‌ها' if fa else 'Overview, daily trends and period comparison')
       subtitle.setStyleSheet('color:#A9C6D3;font-size:12px;')
       health_layout.addWidget(subtitle)
       kpi_grid=QGridLayout()
       kpi_cards=[]
       for i,label in enumerate((['بررسی‌ها','هشدارها','نرخ هشدار','تغییر نسبت به قبل'] if fa else
                                 ['Checks','Warnings','Warning rate','Change vs previous'])):
        frame=QFrame()
        frame.setStyleSheet('QFrame{background:#132F42;border:1px solid #30546A;border-radius:12px;}')
        inner=QVBoxLayout(frame)
        heading_label=QLabel(label)
        heading_label.setStyleSheet('color:#ACC9D7;font-size:12px;')
        value_label=QLabel('—')
        value_label.setStyleSheet('color:#5EEAD4;font-size:25px;font-weight:800;')
        inner.addWidget(heading_label)
        inner.addWidget(value_label)
        kpi_grid.addWidget(frame,i//2,i%2)
        kpi_cards.append(value_label)
       health_layout.addLayout(kpi_grid)
       status_label=QLabel();status_label.setWordWrap(True)
       health_layout.addWidget(status_label)
       health_table=QTableWidget(0,4)
       health_table.setAlternatingRowColors(True)
       health_table.setMinimumHeight(175)
       health_table.setHorizontalHeaderLabels(['زمان','دیتابیس','پایش','خطاها'] if fa else
                                              ['Time','Database','Monitor','Failures'])
       health_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       health_layout.addWidget(QLabel('تاریخچه بررسی‌های اخیر' if fa else 'Recent health checks'))
       health_layout.addWidget(health_table)
       from system_health_overview_v125 import HealthOverviewWorker
       overview_state={'worker':None,'pending':False,'closing':False}
       indicator_label=QLabel()
       health_layout.insertWidget(1,indicator_label)
       overview_progress=QLabel('آماده' if fa else 'Ready')
       health_layout.addWidget(overview_progress)
       def refresh_health():
        if overview_state['closing']:return
        if overview_state['worker'] is not None:
         overview_state['pending']=True
         return
        worker=HealthOverviewWorker(DB,self.user_id,self.session_token,
                                    getattr(self,'_security_monitor_state','unknown'),health_dialog)
        overview_state['worker']=worker
        refresh_btn.setEnabled(False)
        overview_progress.setText('در حال بررسی سلامت…' if fa else 'Checking system health…')
        def succeeded(payload):
         if overview_state['closing']:return
         report=payload['status'];rows=payload['rows'];metrics=payload['metrics']
         status_label.setText((f"دیتابیس: {report['database_status']} | پایش: {report['monitor_state']} | "
                               f"خطاها: {report['failure_count']} | آخرین بررسی سالم: {report['last_healthy_check'] or '—'}"
                               if fa else
                               f"Database: {report['database_status']} | Monitor: {report['monitor_state']} | "
                               f"Failures: {report['failure_count']} | Last healthy check: {report['last_healthy_check'] or '—'}"))
         health_table.setRowCount(len(rows))
         for row_index,row in enumerate(rows):
          for col_index,value in enumerate(row):
           health_table.setItem(row_index,col_index,QTableWidgetItem(str(value)))
         indicator_label.setText((f"شاخص سلامت: {metrics['indicator']} | بررسی‌ها: {metrics['total']} | هشدارها: {metrics['warnings']} ({metrics['warning_rate']}%)"
                                  if fa else f"Health: {metrics['indicator']} | Checks: {metrics['total']} | Warnings: {metrics['warnings']} ({metrics['warning_rate']}%)"))
         overview_progress.setText('بررسی کامل شد' if fa else 'Check completed')
        def failed(_message):
         if not overview_state['closing']:
          overview_progress.setText('بررسی سلامت ناموفق بود' if fa else 'Health check failed')
        def finished():
         overview_state['worker']=None
         worker.deleteLater()
         if overview_state['closing']:return
         refresh_btn.setEnabled(True)
         if overview_state['pending']:
          overview_state['pending']=False
          refresh_health()
        worker.succeeded.connect(succeeded)
        worker.failed.connect(failed)
        worker.finished.connect(finished)
        worker.start()
       # Stage 127: report audit center. Stores only filenames, never full paths.
       from report_center_v127 import list_exports, record_export
       import sqlite3 as _sqlite127
       from custom_report_dialog_v129 import CustomReportDialog
       custom_report_btn=QPushButton('◈ گزارش‌ساز سفارشی' if fa else '◈ Custom Report Builder')
       custom_report_btn.clicked.connect(lambda: CustomReportDialog(DB,self.user_id,self.session_token,'fa' if fa else 'en',health_dialog).exec())
       from operational_report_dialog_v130 import OperationalReportDialog
       operational_report_btn=QPushButton('گزارش‌های عملیاتی هتل' if fa else 'Hotel Operational Reports')
       operational_report_btn.clicked.connect(lambda: OperationalReportDialog(DB,self.user_id,self.session_token,'fa' if fa else 'en',health_dialog).exec())
       health_layout.addWidget(custom_report_btn)
       health_layout.addWidget(operational_report_btn)
       from executive_dashboard_dialog_v131 import ExecutiveDashboardDialog
       executive_btn=QPushButton('داشبورد مدیریتی هوشمند' if fa else 'Executive Dashboard')
       executive_btn.clicked.connect(lambda: ExecutiveDashboardDialog(DB,self.user_id,self.session_token,'fa' if fa else 'en',health_dialog).exec())
       health_layout.addWidget(executive_btn)
       report_heading=QLabel('مرکز مدیریت گزارش‌ها' if fa else 'Report Center')
       report_heading.setStyleSheet('font-size:19px;font-weight:700;color:#5EEAD4;')
       health_layout.addWidget(report_heading)
       report_filters=QHBoxLayout()
       report_search=QLineEdit()
       report_search.setPlaceholderText('جست‌وجوی نام فایل' if fa else 'Search filename')
       report_status_filter=QComboBox()
       for text_,value_ in ([('همه وضعیت‌ها','all'),('موفق','success'),('ناموفق','failed'),('لغوشده','cancelled')] if fa else
                            [('All statuses','all'),('Success','success'),('Failed','failed'),('Cancelled','cancelled')]):
        report_status_filter.addItem(text_,value_)
       report_format_filter=QComboBox()
       for text_,value_ in [('All formats' if not fa else 'همه فرمت‌ها','all'),('PDF','pdf'),('Excel','xlsx')]:
        report_format_filter.addItem(text_,value_)
       report_filters.addWidget(report_search)
       report_filters.addWidget(report_status_filter)
       report_filters.addWidget(report_format_filter)
       health_layout.addLayout(report_filters)
       report_table=QTableWidget(0,6)
       report_table.setAlternatingRowColors(True)
       report_table.setMinimumHeight(180)
       report_table.setHorizontalHeaderLabels(['زمان UTC','فرمت','وضعیت','نام فایل','رکوردها','خطا'] if fa else
                                             ['UTC time','Format','Status','Filename','Records','Error'])
       report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       health_layout.addWidget(report_table)
       report_hint=QLabel('تاریخچه فقط نام فایل را ذخیره می‌کند؛ فایل‌های قبلی خودکار بازتولید نمی‌شوند.' if fa else
                          'History stores filenames only; existing files are not automatically regenerated.')
       report_hint.setWordWrap(True)
       health_layout.addWidget(report_hint)
       def refresh_report_center():
        try:
         with _sqlite127.connect(DB,timeout=5) as report_conn:
          authorize_action(report_conn,self.user_id,self.session_token,'security.view')
          records=list_exports(report_conn,self.user_id,status=report_status_filter.currentData(),
                 fmt=report_format_filter.currentData(),search=report_search.text().strip())
         report_table.setRowCount(len(records))
         for r_index,record in enumerate(records):
          for c_index,value in enumerate(record):
           report_table.setItem(r_index,c_index,QTableWidgetItem(str(value)))
         report_hint.setText((f'{len(records)} گزارش ثبت‌شده' if fa else f'{len(records)} recorded exports'))
        except (PermissionError,ValueError,_sqlite127.Error):
         report_hint.setText('خواندن تاریخچه ممکن نیست' if fa else 'Unable to load report history')
       def audit_export(fmt,status,filename,count=0,error_code=''):
        try:
         with _sqlite127.connect(DB,timeout=5) as audit_conn:
          authorize_action(audit_conn,self.user_id,self.session_token,'security.view')
          record_export(audit_conn,self.user_id,fmt=fmt,status=status,
                        filename=filename,record_count=count,error_code=error_code)
        except (PermissionError,ValueError,_sqlite127.Error):
         pass  # Do not change the outcome of an already completed export.
        refresh_report_center()
       report_refresh=QPushButton('به‌روزرسانی تاریخچه' if fa else 'Refresh history')
       report_refresh.clicked.connect(refresh_report_center)
       health_layout.addWidget(report_refresh)
       report_status_filter.currentIndexChanged.connect(lambda _:refresh_report_center())
       report_format_filter.currentIndexChanged.connect(lambda _:refresh_report_center())
       report_search.textChanged.connect(lambda _:refresh_report_center())
       from system_health_export_v126 import HealthExportWorker
       export_state={'worker':None,'closing':False}
       export_status=QLabel('آماده خروجی‌گیری' if fa else 'Export ready')
       export_progress=QProgressBar()
       export_progress.setRange(0,100)
       export_progress.setValue(0)
       health_layout.addWidget(export_status)
       health_layout.addWidget(export_progress)
       def export_health(fmt):
        if export_state['closing'] or export_state['worker'] is not None:return
        filename,_=QFileDialog.getSaveFileName(health_dialog,
          'خروجی سلامت سیستم' if fa else 'Export system health',
          'system_health.'+fmt, 'Excel Workbook (*.xlsx)' if fmt=='xlsx' else 'PDF (*.pdf)')
        if not filename:return
        if not filename.lower().endswith('.'+fmt):filename+='.'+fmt
        worker=HealthExportWorker(DB,self.user_id,self.session_token,filename,fmt,
                                  'fa' if fa else 'en',health_dialog)
        export_state['worker']=worker
        export_progress.setValue(0)
        export_status.setText('در حال تولید گزارش…' if fa else 'Generating report…')
        excel_btn.setEnabled(False);pdf_btn.setEnabled(False)
        cancel_export_btn.setEnabled(True)
        def success(_count):
         if export_state['closing']:return
         audit_export(fmt,'success',filename,_count)
         export_status.setText('گزارش ذخیره شد' if fa else 'Report saved')
        def failure(message):
         if export_state['closing']:return
         audit_export(fmt,'failed',filename,error_code='unexpected')
         export_status.setText('خروجی ناموفق بود' if fa else 'Export failed')
         QMessageBox.warning(health_dialog,'Error',message)
        def cancelled():
         if not export_state['closing']:
          audit_export(fmt,'cancelled',filename,error_code='cancelled')
          export_status.setText('خروجی لغو شد' if fa else 'Export cancelled')
        def finished():
         export_state['worker']=None
         worker.deleteLater()
         if not export_state['closing']:
          excel_btn.setEnabled(True);pdf_btn.setEnabled(True)
          cancel_export_btn.setEnabled(False)
        worker.progress.connect(export_progress.setValue)
        worker.succeeded.connect(success)
        worker.failed.connect(failure)
        worker.cancelled.connect(cancelled)
        worker.finished.connect(finished)
        worker.start()
       def cancel_export():
        worker=export_state['worker']
        if worker is not None:
         worker.cancel()
         export_status.setText('در حال لغو…' if fa else 'Cancelling…')
       export_row=QHBoxLayout()
       excel_btn=QPushButton('خروجی Excel' if fa else 'Export Excel')
       pdf_btn=QPushButton('خروجی PDF' if fa else 'Export PDF')
       excel_btn.clicked.connect(lambda:export_health('xlsx'))
       pdf_btn.clicked.connect(lambda:export_health('pdf'))
       cancel_export_btn=QPushButton('لغو خروجی' if fa else 'Cancel export')
       cancel_export_btn.setEnabled(False)
       cancel_export_btn.clicked.connect(cancel_export)
       export_row.addWidget(excel_btn);export_row.addWidget(pdf_btn);export_row.addWidget(cancel_export_btn)
       health_layout.addLayout(export_row)
       refresh_btn=QPushButton('بررسی مجدد' if fa else 'Run health check')
       refresh_btn.clicked.connect(refresh_health)
       health_layout.addWidget(refresh_btn)
       # Stage 121: read-only, UTC-bounded comparative analytics.
       from system_health_analytics_v121 import compare_periods
       analysis_row=QHBoxLayout()
       analysis_days=QSpinBox();analysis_days.setRange(1,90);analysis_days.setValue(7)
       analysis_threshold=QSpinBox();analysis_threshold.setRange(0,100);analysis_threshold.setSuffix('%');analysis_threshold.setValue(20)
       analysis_row.addWidget(QLabel('بازه (روز)' if fa else 'Period (days)'))
       analysis_row.addWidget(analysis_days)
       analysis_row.addWidget(QLabel('آستانه هشدار' if fa else 'Alert threshold'))
       analysis_row.addWidget(analysis_threshold)
       analysis_button=QPushButton('مقایسه دوره‌ها' if fa else 'Compare periods')
       analysis_row.addWidget(analysis_button)
       health_layout.addLayout(analysis_row)
       # Stage 128: per-admin saved analysis presets; no guest data is persisted.
       from report_preferences_v128 import save_preset, list_presets, delete_preset
       preset_row=QHBoxLayout()
       preset_selector=QComboBox()
       preset_selector.setMinimumWidth(150)
       preset_name=QLineEdit()
       preset_name.setMaxLength(40)
       preset_name.setPlaceholderText('نام تنظیمات' if fa else 'Preset name')
       preset_save=QPushButton('ذخیره تنظیمات' if fa else 'Save preset')
       preset_apply=QPushButton('اعمال' if fa else 'Apply')
       preset_delete=QPushButton('حذف' if fa else 'Delete')
       preset_row.addWidget(preset_selector)
       preset_row.addWidget(preset_name)
       preset_row.addWidget(preset_save)
       preset_row.addWidget(preset_apply)
       preset_row.addWidget(preset_delete)
       health_layout.addLayout(preset_row)
       def load_presets():
        with _sqlite127.connect(DB,timeout=5) as db:
         authorize_action(db,self.user_id,self.session_token,'security.view')
         presets=list_presets(db,self.user_id)
        preset_selector.clear()
        for name,days,threshold in presets:
         preset_selector.addItem(name,(days,threshold))
       def save_current_preset():
        try:
         with _sqlite127.connect(DB,timeout=5) as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          save_preset(db,self.user_id,preset_name.text().strip(),analysis_days.value(),analysis_threshold.value())
         load_presets()
         idx=preset_selector.findText(preset_name.text().strip())
         if idx>=0:preset_selector.setCurrentIndex(idx)
        except (PermissionError,ValueError,_sqlite127.Error) as error:
         QMessageBox.warning(health_dialog,'Preset',str(error))
       def apply_selected_preset():
        value=preset_selector.currentData()
        if value is None:return
        analysis_days.setValue(value[0]);analysis_threshold.setValue(value[1])
       def delete_selected_preset():
        name=preset_selector.currentText()
        if not name:return
        try:
         with _sqlite127.connect(DB,timeout=5) as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          delete_preset(db,self.user_id,name)
         load_presets()
        except (PermissionError,ValueError,_sqlite127.Error) as error:
         QMessageBox.warning(health_dialog,'Preset',str(error))
       preset_save.clicked.connect(save_current_preset)
       preset_apply.clicked.connect(apply_selected_preset)
       preset_delete.clicked.connect(delete_selected_preset)
       try:load_presets()
       except (PermissionError,_sqlite127.Error):
        preset_save.setEnabled(False);preset_apply.setEnabled(False);preset_delete.setEnabled(False)

       analysis_label=QLabel();analysis_label.setWordWrap(True)
       health_layout.addWidget(analysis_label)
       # Stage 122: UTC daily trends, colored warning-rate chart and hover details.
       from system_health_trends_v122 import daily_trends
       from system_health_chart_v122 import HealthTrendChart
       health_chart=HealthTrendChart(health_dialog)
       health_chart.setMinimumHeight(220)
       health_layout.addWidget(health_chart)
       chart_legend=QLabel('سبز: زیر آستانه | قرمز: عبور از آستانه | خط زرد: آستانه' if fa else
                           'Teal: below threshold | Red: threshold reached | Dashed yellow: threshold')
       chart_legend.setStyleSheet('color:#b7ced9;')
       health_layout.addWidget(chart_legend)
       analysis_table=QTableWidget(0,3)
       analysis_table.setAlternatingRowColors(True)
       analysis_table.setMinimumHeight(160)
       analysis_table.setHorizontalHeaderLabels(['شاخص','دوره فعلی','دوره قبل'] if fa else ['Metric','Current','Previous'])
       analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       health_layout.addWidget(analysis_table)
       from system_health_async_v124 import HealthDashboardWorker
       comparison_state={'worker':None,'pending':False,'closing':False}
       loading_label=QLabel('آماده' if fa else 'Ready')
       loading_label.setStyleSheet('color:#A9C6D3;')
       health_layout.addWidget(loading_label)
       debounce=QTimer(health_dialog)
       debounce.setSingleShot(True)
       debounce.setInterval(250)
       def refresh_comparison():
        if comparison_state['closing']:
         return
        if comparison_state['worker'] is not None:
         comparison_state['pending']=True
         loading_label.setText('در انتظار به‌روزرسانی…' if fa else 'Update queued…')
         return
        days=analysis_days.value()
        threshold=analysis_threshold.value()
        worker=HealthDashboardWorker(DB,self.user_id,self.session_token,days,threshold,health_dialog)
        comparison_state['worker']=worker
        comparison_state['pending']=False
        analysis_button.setEnabled(False)
        loading_label.setText('در حال بارگذاری…' if fa else 'Loading…')
        def succeeded(payload):
         if comparison_state['closing']:
          return
         if payload['days'] != analysis_days.value() or payload['threshold'] != analysis_threshold.value():
          comparison_state['pending']=True
          return
         loading_label.setText('به‌روز شد' if fa else 'Updated')
         result=payload['result']
         series=payload['series']
         apply_comparison(result,series,payload['threshold'])
        def failed(message):
         if not comparison_state['closing']:
          loading_label.setText('خطا در بارگذاری اطلاعات' if fa else message)
        def finished():
         comparison_state['worker']=None
         worker.deleteLater()
         if comparison_state['closing']:
          return
         analysis_button.setEnabled(True)
         if comparison_state['pending']:
          comparison_state['pending']=False
          debounce.start()
        worker.succeeded.connect(succeeded)
        worker.failed.connect(failed)
        worker.finished.connect(finished)
        worker.start()
       def apply_comparison(result,series,threshold):
         health_chart.set_series(series,threshold,'fa' if fa else 'en')
         current=result['current']
         kpi_values=[str(current['checks']),str(current['warnings']),
                     f"{current['warning_rate']:.1f}%",f"{result['warning_rate_delta']:+.1f} pp"]
         for widget,value in zip(kpi_cards,kpi_values):
          widget.setText(value)
         kpi_cards[2].setStyleSheet('color:#FCA5A5;font-size:25px;font-weight:800;' if
          current['checks'] and current['warning_rate']>=threshold else
          'color:#5EEAD4;font-size:25px;font-weight:800;')
         alert_labels={'no_recent_checks':('هیچ بررسی جدیدی ثبت نشده','No recent checks'),
           'warning_rate_threshold':('نرخ هشدار از آستانه عبور کرده','Warning rate exceeds threshold'),
           'database_warning':('آخرین وضعیت دیتابیس هشدار دارد','Latest database check warns'),
           'monitor_warning':('آخرین وضعیت پایش هشدار دارد','Latest monitor state warns')}
         warnings=', '.join(alert_labels[a][0 if fa else 1] for a in result['alerts']) or ('بدون هشدار' if fa else 'No alerts')
         analysis_label.setText((f'هشدارها: {warnings} | تغییر نرخ هشدار: {result["warning_rate_delta"]:+.1f}٪' if fa else
             f'Alerts: {warnings} | Warning-rate change: {result["warning_rate_delta"]:+.1f}%'))
         analysis_label.setStyleSheet('color:#FBBF24;font-weight:700;' if result['alerts'] else 'color:#5EEAD4;font-weight:700;')
         values=[('بررسی‌ها' if fa else 'Checks','checks'),('هشدارها' if fa else 'Warnings','warnings'),
                 ('نرخ هشدار (%)' if fa else 'Warning rate (%)','warning_rate'),
                 ('بیشترین خطا' if fa else 'Maximum failures','max_failures')]
         analysis_table.setRowCount(len(values))
         for idx,(label,key) in enumerate(values):
          for col,value in enumerate((label,result['current'][key],result['previous'][key])):
           analysis_table.setItem(idx,col,QTableWidgetItem(str(value)))
       analysis_button.clicked.connect(refresh_comparison)
       analysis_days.valueChanged.connect(lambda _value:debounce.start())
       analysis_threshold.valueChanged.connect(lambda _value:debounce.start())
       debounce.timeout.connect(refresh_comparison)
       def close_health_dialog(event):
        overview_state['closing']=True
        comparison_state['closing']=True
        export_state['closing']=True
        overview_worker=overview_state['worker']
        if overview_worker is not None and overview_worker.isRunning():
         overview_worker.cancel()
         if not overview_worker.wait(6000):
          overview_state['closing']=False
          comparison_state['closing']=False
          export_state['closing']=False
          event.ignore()
          return
        debounce.stop()
        worker=comparison_state['worker']
        if worker is not None and worker.isRunning():
         worker.cancel()
         if not worker.wait(6000):
          overview_state['closing']=False
          comparison_state['closing']=False
          export_state['closing']=False
          event.ignore()
          return
        export_worker=export_state['worker']
        if export_worker is not None and export_worker.isRunning():
         export_worker.cancel()
         if not export_worker.wait(6000):
          overview_state['closing']=False
          comparison_state['closing']=False
          export_state['closing']=False
          event.ignore()
          return
        event.accept()
       health_dialog.closeEvent=close_health_dialog
       def safe_reject():
        export_worker=export_state['worker']
        if export_worker is not None and export_worker.isRunning():
         export_worker.cancel()
         export_status.setText('در حال لغو…' if fa else 'Cancelling…')
         return
        overview_worker=overview_state['worker']
        if overview_worker is not None and overview_worker.isRunning():
         overview_worker.cancel()
         overview_progress.setText('در حال لغو…' if fa else 'Cancelling…')
         return
        worker=comparison_state['worker']
        if worker is not None and worker.isRunning():
         worker.cancel()
         loading_label.setText('در حال لغو…' if fa else 'Cancelling…')
         return
        health_dialog.done(QDialog.DialogCode.Rejected)
       health_dialog.reject=safe_reject
       refresh_report_center()
       refresh_health()
       refresh_comparison()
       health_dialog.exec()
      health_btn.clicked.connect(show_system_health)
      v.addWidget(health_btn)
      v.addWidget(QLabel('گزارش ۷ روز اخیر (UTC)' if fa else 'Last 7 days (UTC)'))
      changes=recent_security_changes(c,self.user_id,limit=15)
      v.addWidget(QLabel('آخرین تغییرات امنیتی' if fa else 'Recent security changes'))
      v.addWidget(self.table(['زمان','مدیر','کاربر','رویداد'] if fa else ['Time','Actor','User','Event'],changes))
      records=list_accounts(c,self.user_id)
      from security_admin_presentation import account_rows, account_counts
      counts=account_counts(records)
      summary_line=QLabel(('حساب‌های فعال: {active} | غیرفعال: {disabled} | مدیران فعال: {admins}' if fa else
         'Active: {active} | Disabled: {disabled} | Active admins: {admins}').format(**counts))
      summary_line.setStyleSheet('font-weight:700;color:#99F6E4;padding:8px;')
      v.addWidget(summary_line)
      search=QLineEdit()
      search.setClearButtonEnabled(True)
      search.setPlaceholderText('جست‌وجوی نام کاربری یا نقش…' if fa else 'Search username or role…')
      v.addWidget(search)
      accounts_table=self.table(
       ['نام کاربری','نقش','وضعیت'] if fa else ['Username','Role','Status'],
       account_rows(records,fa=fa))
      v.addWidget(accounts_table)
      def filter_accounts(query):
       needle=query.strip().casefold()
       for row in range(accounts_table.rowCount()):
        fields=[accounts_table.item(row,col).text().casefold() for col in range(accounts_table.columnCount()) if accounts_table.item(row,col)]
        accounts_table.setRowHidden(row,bool(needle) and not any(needle in field for field in fields))
      search.textChanged.connect(filter_accounts)
      selector=QComboBox()
      for uid,name,role,active in records:
       selector.addItem(f'{name}  |  {role}  |  {"Active" if active else "Disabled"}',uid)
      v.addWidget(selector)
      controls=QHBoxLayout()
      create_button=QPushButton('＋ ایجاد کاربر' if fa else '＋ Add user')
      create_button.clicked.connect(self.create_user);controls.addWidget(create_button)
      def modify(action):
       from security_action_service import execute_admin_action
       target=selector.currentData()
       if target is None:return
       try:
        with connect() as db:
         if action=='toggle':
          state=db.execute('SELECT active FROM users WHERE id=?',(target,)).fetchone()
          execute_admin_action(db,self.user_id,self.session_token,'account.toggle',target,value=not bool(state[0]))
         elif action=='role':
          role,ok=QInputDialog.getItem(self,'نقش' if fa else 'Role','نقش:' if fa else 'Role:', ['reception','admin'],0,False)
          if not ok:return
          execute_admin_action(db,self.user_id,self.session_token,'account.role',target,value=role)
         elif action=='password':
          first,ok=QInputDialog.getText(self,'رمز جدید' if fa else 'New password','رمز عبور:' if fa else 'Password:',QLineEdit.EchoMode.Password)
          if not ok:return
          again,ok=QInputDialog.getText(self,'تکرار رمز' if fa else 'Confirm password','تکرار:' if fa else 'Confirm:',QLineEdit.EchoMode.Password)
          if not ok:return
          execute_admin_action(db,self.user_id,self.session_token,'account.password',target,value=first,confirmation=again)
        self.navigate(15)
       except (ValueError,PermissionError,sqlite3.Error) as exc:
        QMessageBox.warning(self,'خطا' if fa else 'Error',str(exc))
      for action,fa_label,en_label in (
       ('toggle','فعال / غیرفعال','Enable / Disable'),
       ('role','تغییر نقش','Change role'),
       ('password','بازنشانی رمز','Reset password')):
       button=QPushButton(fa_label if fa else en_label)
       button.clicked.connect(lambda checked=False,a=action:modify(a))
       controls.addWidget(button)
      v.addLayout(controls)
      from security_sessions import recent_login_events,list_sessions,revoke_user_sessions
      history=QPushButton('تاریخچه ورود' if fa else 'Login history')
      def show_history():
       if not self.authorize_operation('users.create'):return
       with connect() as db:entries=recent_login_events(db,self.user_id)
       box=QDialog(self);box.setWindowTitle('تاریخچه ورود' if fa else 'Login history')
       box.resize(700,450);lay=QVBoxLayout(box)
       lay.addWidget(self.table(['زمان','کاربر','نتیجه'] if fa else ['Time','User','Outcome'],entries))
       box.exec()
      history.clicked.connect(show_history);v.addWidget(history)
      sessions=QPushButton('نشست‌های کاربر' if fa else 'User sessions')
      def show_sessions():
       if not self.authorize_operation('users.create'):return
       target=selector.currentData()
       if target is None:return
       with connect() as db:entries=list_sessions(db,self.user_id,target)
       box=QDialog(self);box.setWindowTitle('نشست‌ها' if fa else 'Sessions')
       box.resize(860,460);lay=QVBoxLayout(box)
       lay.addWidget(self.table(['شناسه','شروع','انقضا','لغو','آخرین فعالیت'] if fa else
         ['ID','Created','Expires','Revoked','Last activity'],entries))
       revoke=QPushButton('لغو تمام نشست‌های این کاربر' if fa else 'Revoke all user sessions')
       def revoke_all():
        if QMessageBox.question(box,'Confirm','Revoke all sessions?')!=QMessageBox.StandardButton.Yes:return
        from security_action_service import execute_admin_action
        with connect() as db:execute_admin_action(db,self.user_id,self.session_token,'session.revoke',target)
        box.accept()
       revoke.clicked.connect(revoke_all);lay.addWidget(revoke);box.exec()
      sessions.clicked.connect(show_sessions);v.addWidget(sessions)
      from permission_policy import ALL_PERMISSIONS,ADMIN_RESERVED,get_overrides,effective_permissions,set_override
      permission_button=QPushButton('مدیریت مجوزهای اختصاصی' if fa else 'Edit individual permissions')
      def edit_permissions():
       target=selector.currentData()
       if target is None:return
       with connect() as db:
        role_row=db.execute('SELECT role FROM users WHERE id=?',(target,)).fetchone()
        overrides=get_overrides(db,self.user_id,target)
       if role_row is None:return
       dialog=QDialog(self)
       dialog.setWindowTitle('مجوزهای کاربر' if fa else 'User permissions')
       dialog.resize(560,480)
       layout=QVBoxLayout(dialog)
       layout.addWidget(QLabel('حساب مدیر از مجوزهای ثابت نقش استفاده می‌کند.' if fa else
                              'Administrator privileges are controlled by role.'))
       options=QComboBox()
       editable=sorted(ALL_PERMISSIONS-ADMIN_RESERVED)
       for permission in editable:options.addItem(permission,permission)
       layout.addWidget(options)
       state=QComboBox()
       state.addItem('پیش‌فرض نقش' if fa else 'Role default',None)
       state.addItem('مجاز' if fa else 'Allow',True)
       state.addItem('غیرمجاز' if fa else 'Deny',False)
       layout.addWidget(state)
       current=QLabel();layout.addWidget(current)
       def update_choice():
        permission=options.currentData()
        override=overrides.get(permission)
        idx=next((j for j in range(state.count()) if state.itemData(j)==(bool(override) if override is not None else None)),0)
        state.setCurrentIndex(idx)
        with connect() as db:enabled=permission in effective_permissions(db,target)
        current.setText(('مجوز مؤثر: ' if fa else 'Effective permission: ')+('✓' if enabled else '✕'))
       options.currentIndexChanged.connect(lambda _:update_choice())
       update_choice()
       save=QPushButton('ذخیره مجوز' if fa else 'Save permission')
       def save_permission():
        try:
         from operation_guard import authorize_action
         with connect() as db:
          authorize_action(db,self.user_id,self.session_token,'users.create')
          set_override(db,self.user_id,target,options.currentData(),state.currentData())
         dialog.accept()
         self.navigate(15)
        except (PermissionError,ValueError,sqlite3.Error) as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       save.clicked.connect(save_permission)
       save.setEnabled(role_row[0]!='admin')
       layout.addWidget(save)
       dialog.exec()
      permission_button.clicked.connect(edit_permissions)
      v.addWidget(permission_button)
      audit_buttons=QHBoxLayout()
      activity_button=QPushButton('تحلیل تلاش‌های ورود' if fa else 'Login activity analytics')
      def open_activity():
       from security_analytics_v109 import security_activity
       dialog=QDialog(self);dialog.setWindowTitle('تحلیل امنیت ورود' if fa else 'Login security analytics')
       dialog.resize(850,550);layout=QVBoxLayout(dialog)
       days=QComboBox()
       for number in (1,7,30,90):days.addItem(str(number)+' '+('روز' if fa else 'days'),number)
       days.setCurrentIndex(1);layout.addWidget(days)
       search=QLineEdit();search.setPlaceholderText('نام کاربری (اختیاری)' if fa else 'Username (optional)')
       layout.addWidget(search)
       from security_monitor_v116 import get_settings,set_settings
       monitor_row=QHBoxLayout()
       monitor_enabled=QCheckBox('پایش دوره‌ای امنیت' if fa else 'Periodic security monitoring')
       monitor_interval=QSpinBox();monitor_interval.setRange(1,60)
       monitor_interval.setSuffix(' دقیقه' if fa else ' min')
       with connect() as monitor_db:
        config=get_settings(monitor_db,self.user_id)
       monitor_enabled.setChecked(config['enabled'])
       monitor_interval.setValue(config['interval_seconds']//60)
       monitor_row.addWidget(monitor_enabled);monitor_row.addWidget(monitor_interval)
       monitor_save=QPushButton('ذخیره پایش' if fa else 'Save monitoring')
       def save_monitor():
        try:
         from operation_guard import authorize_action
         with connect() as monitor_db:
          authorize_action(monitor_db,self.user_id,self.session_token,'security.view')
          set_settings(monitor_db,self.user_id,enabled=monitor_enabled.isChecked(),
                       interval_seconds=monitor_interval.value()*60)
         self.start_security_monitor()
        except (PermissionError,ValueError,sqlite3.Error) as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       monitor_save.clicked.connect(save_monitor)
       monitor_row.addWidget(monitor_save);layout.addLayout(monitor_row)
       monitor_status=QLabel();monitor_status.setWordWrap(True)
       layout.addWidget(monitor_status)
       def refresh_monitor_status():
        from security_monitor_status_v118 import list_failures
        state=getattr(self,'_security_monitor_state','idle')
        attempt=getattr(self,'_security_monitor_retry_attempt',0)
        monitor_status.setText((f'وضعیت پایش: {state} | تلاش مجدد: {attempt}' if fa else
                                f'Monitor: {state} | retry: {attempt}'))
        try:
         with connect() as status_db:rows=list_failures(status_db,self.user_id,5)
         monitor_history.setText(('خطاهای اخیر: ' if fa else 'Recent failures: ')+
                                 (' | '.join(f'{stamp[:19]} {category}' for stamp,category,_ in rows) or ('ندارد' if fa else 'None')))
        except (PermissionError,sqlite3.Error,ValueError):
         monitor_history.setText('—')
       monitor_history=QLabel();monitor_history.setWordWrap(True)
       layout.addWidget(monitor_history)
       monitor_refresh=QPushButton('بروزرسانی وضعیت' if fa else 'Refresh monitor status')
       monitor_refresh.clicked.connect(refresh_monitor_status)
       layout.addWidget(monitor_refresh)
       refresh_monitor_status()
       from security_chart_widget_v111 import SecurityTrendChart
       trend_chart=SecurityTrendChart(dialog);layout.addWidget(trend_chart)
       legend=QLabel(('سبز: موفق | زرد: ناموفق | قرمز: مسدود' if fa else
                      'Green: success | Amber: failure | Red: locked'))
       legend.setStyleSheet('color:#b9cad8;padding:4px;');layout.addWidget(legend)
       from security_alerts_v113 import get_threshold,set_threshold,evaluate_and_record,alert_history
       alert_bar=QHBoxLayout()
       alert_bar.addWidget(QLabel('آستانه هشدار' if fa else 'Alert threshold'))
       alert_threshold=QSpinBox();alert_threshold.setRange(1,100)
       with connect() as alert_db:alert_threshold.setValue(get_threshold(alert_db,self.user_id))
       alert_bar.addWidget(alert_threshold)
       save_alert=QPushButton('ذخیره آستانه' if fa else 'Save threshold')
       def save_threshold():
        try:
         from operation_guard import authorize_action
         with connect() as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          set_threshold(db,self.user_id,alert_threshold.value())
         refresh()
        except (PermissionError,ValueError,sqlite3.Error) as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       save_alert.clicked.connect(save_threshold)
       alert_bar.addWidget(save_alert);layout.addLayout(alert_bar)
       alert_status=QLabel();alert_status.setWordWrap(True)
       alert_status.setStyleSheet('padding:9px;border-radius:8px;background:#152D40;color:#FBBF24;')
       layout.addWidget(alert_status)
       notifications_button=QPushButton('مرکز اعلان‌های امنیتی' if fa else 'Security notification center')
       def open_notifications():
        from security_notifications_v114 import sync_alerts,inbox,mark_read,acknowledge,archive,restore
        popup=QDialog(dialog);popup.setWindowTitle('اعلان‌های امنیتی' if fa else 'Security notifications')
        popup.resize(940,500);pv=QVBoxLayout(popup)
        filters=QHBoxLayout();status_filter=QComboBox()
        for title,key in ([('همه','all'),('خوانده‌نشده','unread'),('خوانده‌شده','read'),('بررسی‌شده','acknowledged'),('بایگانی','archived')] if fa else
                          [('All','all'),('Unread','unread'),('Read','read'),('Acknowledged','acknowledged'),('Archived','archived')]):
         status_filter.addItem(title,key)
        filters.addWidget(status_filter);pv.addLayout(filters)
        notifications_table=QTableWidget();notifications_table.setColumnCount(7)
        notifications_table.setHorizontalHeaderLabels(['شناسه','زمان','کاربر','شدت','تلاش‌ها','خوانده‌شده','تأیید بررسی'] if fa else
                                                      ['ID','Time','User','Severity','Attempts','Read','Acknowledged'])
        notifications_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        notifications_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        pv.addWidget(notifications_table)
        def load_notifications():
         try:
          from operation_guard import authorize_action
          with connect() as db:
           authorize_action(db,self.user_id,self.session_token,'security.view')
           sync_alerts(db,self.user_id)
           rows=inbox(db,self.user_id,status=status_filter.currentData())
          notifications_table.setRowCount(len(rows))
          for ri,values in enumerate(rows):
           for ci,value in enumerate(values):
            notifications_table.setItem(ri,ci,QTableWidgetItem(str(value if value is not None else '')))
         except (PermissionError,ValueError,sqlite3.Error) as exc:
          QMessageBox.warning(popup,'خطا' if fa else 'Error',str(exc))
        def change_notification(ack=False, archive_action=None):
         selected=notifications_table.currentRow()
         if selected<0:return
         item=notifications_table.item(selected,0)
         if item is None:return
         try:
          from operation_guard import authorize_action
          with connect() as db:
           authorize_action(db,self.user_id,self.session_token,'security.view')
           action=(archive if archive_action=='archive' else restore if archive_action=='restore' else acknowledge if ack else mark_read)
           action(db,self.user_id,int(item.text()))
          load_notifications();update_notification_badge()
         except (PermissionError,ValueError,sqlite3.Error) as exc:
          QMessageBox.warning(popup,'خطا' if fa else 'Error',str(exc))
        status_filter.currentIndexChanged.connect(load_notifications)
        actions=QHBoxLayout()
        read_button=QPushButton('علامت‌گذاری خوانده‌شده' if fa else 'Mark as read')
        ack_button=QPushButton('تأیید بررسی' if fa else 'Acknowledge')
        read_button.clicked.connect(lambda:change_notification(False))
        ack_button.clicked.connect(lambda:change_notification(True))
        archive_button=QPushButton('بایگانی' if fa else 'Archive')
        restore_button=QPushButton('بازگردانی' if fa else 'Restore')
        archive_button.clicked.connect(lambda:change_notification(archive_action='archive'))
        restore_button.clicked.connect(lambda:change_notification(archive_action='restore'))
        actions.addWidget(read_button);actions.addWidget(ack_button)
        actions.addWidget(archive_button);actions.addWidget(restore_button);pv.addLayout(actions)
        load_notifications();popup.exec()
       def update_notification_badge():
        try:
         from security_notifications_v114 import sync_alerts
         from operation_guard import authorize_action
         with connect() as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          count=sync_alerts(db,self.user_id)
         notifications_button.setText(('اعلان‌های امنیتی' if fa else 'Security notifications')+f' ({count})')
        except (PermissionError,ValueError,sqlite3.Error):
         notifications_button.setEnabled(False)
       self.open_security_notifications=open_notifications
       notifications_button.clicked.connect(open_notifications)
       layout.addWidget(notifications_button)
       history_bar=QHBoxLayout()
       severity_filter=QComboBox()
       severity_filter.addItem('همه هشدارها' if fa else 'All alerts',None)
       severity_filter.addItem('شدید' if fa else 'High','high')
       severity_filter.addItem('نیازمند بررسی' if fa else 'Review','review')
       history_bar.addWidget(severity_filter)
       history_button=QPushButton('تاریخچه هشدارها' if fa else 'Alert history')
       def show_alert_history():
        try:
         from operation_guard import authorize_action
         with connect() as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          rows=alert_history(db,self.user_id,severity=severity_filter.currentData())
         popup=QDialog(dialog);popup.setWindowTitle('تاریخچه هشدارهای امنیتی' if fa else 'Security alert history')
         popup.resize(900,460);popup_layout=QVBoxLayout(popup)
         table=QTableWidget();table.setColumnCount(7);table.setRowCount(len(rows))
         table.setHorizontalHeaderLabels(['زمان','کاربر','روز','شدت','تلاش‌ها','بازه قبل','آستانه'] if fa else
                                          ['Time','User','Days','Severity','Attempts','Previous','Threshold'])
         table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
         for ri,values in enumerate(rows):
          for ci,value in enumerate(values):table.setItem(ri,ci,QTableWidgetItem(str(value)))
         popup_layout.addWidget(table);popup.exec()
        except (PermissionError,ValueError,sqlite3.Error) as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       history_button.clicked.connect(show_alert_history)
       history_bar.addWidget(history_button);layout.addLayout(history_bar)
       summary=QLabel();summary.setStyleSheet('font-weight:700;color:#e5f3ff;padding:8px;')
       layout.addWidget(summary)
       result_table=QTableWidget();result_table.setColumnCount(3)
       result_table.setHorizontalHeaderLabels(['زمان','کاربر','نتیجه'] if fa else ['Time','User','Outcome'])
       result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
       layout.addWidget(result_table)
       review=QLabel();review.setWordWrap(True);layout.addWidget(review)
       def refresh():
        try:
         with connect() as db:
          from operation_guard import authorize_action
          authorize_action(db,self.user_id,self.session_token,'security.view')
          data=security_activity(db,self.user_id,days=days.currentData(),username=search.text().strip() or None)
         from security_chart_v111 import chart_data
         with connect() as db:
          chart=chart_data(db,self.user_id,days=days.currentData(),username=search.text().strip() or None)
         trend_chart.set_series(chart['series'])
         with connect() as db:
          from operation_guard import authorize_action
          authorize_action(db,self.user_id,self.session_token,'security.view')
          signal=evaluate_and_record(db,self.user_id,days=days.currentData(),username=search.text().strip() or None)
         update_notification_badge()
         level=signal['alert']
         alert_status.setText((('وضعیت هشدار: ' if fa else 'Alert status: ')+
            ({'high':'شدید','review':'نیازمند بررسی','normal':'عادی'}[level] if fa else level.upper())+
            (' | تغییر تلاش‌های ناموفق: ' if fa else ' | Failure delta: ')+str(signal['failed_delta'])))
         totals=data['totals']
         summary.setText((f"موفق: {totals['success']} | ناموفق: {totals['failure']} | مسدود: {totals['locked']}" if fa else
                          f"Success: {totals['success']} | Failure: {totals['failure']} | Locked: {totals['locked']}") +
                         (f" | نرخ موفقیت: {chart['success_rate']}٪" if fa else f" | Success rate: {chart['success_rate']}%"))
         result_table.setRowCount(len(data['records']))
         for row,record in enumerate(data['records']):
          for col,value in enumerate(record):result_table.setItem(row,col,QTableWidgetItem(str(value)))
         review.setText(('نیازمند بررسی: ' if fa else 'Review candidates: ')+', '.join(f'{name} ({count})' for name,count in data['review_candidates']))
        except (PermissionError,ValueError,sqlite3.Error) as exc:QMessageBox.warning(dialog,'Error',str(exc))
       refresh_button=QPushButton('بروزرسانی' if fa else 'Refresh');refresh_button.clicked.connect(refresh)
       layout.addWidget(refresh_button)
       pdf_button=QPushButton('خروجی PDF امنیتی' if fa else 'Export security PDF')
       def export_security_pdf():
        path,_=QFileDialog.getSaveFileName(dialog,'PDF','security-report.pdf','PDF (*.pdf)')
        if not path:return
        try:
         from security_report_v110 import write_security_pdf
         from operation_guard import authorize_action
         with connect() as db:
          authorize_action(db,self.user_id,self.session_token,'security.view')
          write_security_pdf(path,db,self.user_id,days=days.currentData(),
                             username=search.text().strip() or None,language=self.language)
         QMessageBox.information(dialog,'موفق' if fa else 'Success','PDF ذخیره شد.' if fa else 'PDF saved.')
        except (PermissionError,ValueError,sqlite3.Error,OSError,ImportError) as exc:
         QMessageBox.warning(dialog,'خطا' if fa else 'Error',str(exc))
       pdf_button.clicked.connect(export_security_pdf)
       layout.addWidget(pdf_button);refresh();dialog.exec()
      activity_button.clicked.connect(open_activity)
      v.addWidget(activity_button)
      permission_history_button=QPushButton('تاریخچه تغییر مجوزها' if fa else 'Permission change history')
      export_permission_history_button=QPushButton('خروجی CSV تاریخچه' if fa else 'Export history CSV')
      def load_permission_history():
       from permission_audit import recent_changes
       try:
        with connect() as db:rows=recent_changes(db,self.user_id,target_id=selector.currentData(),limit=100)
        history_dialog=QDialog(self);history_dialog.setWindowTitle('تاریخچه مجوزها' if fa else 'Permission history')
        history_dialog.resize(900,500);history_layout=QVBoxLayout(history_dialog)
        history_layout.addWidget(self.table(
         ['زمان','مدیر','کاربر','مجوز','مقدار قبلی','مقدار جدید'] if fa else
         ['Time','Actor','User','Permission','Previous','New'],rows))
        history_dialog.exec()
       except (PermissionError,ValueError,sqlite3.Error) as exc:
        QMessageBox.warning(self,'خطا' if fa else 'Error',str(exc))
      def export_permission_history():
       from permission_audit import recent_changes,export_changes_csv
       path,_=QFileDialog.getSaveFileName(self,'CSV','permission_history.csv','CSV (*.csv)')
       if not path:return
       try:
        with connect() as db:rows=recent_changes(db,self.user_id,target_id=selector.currentData(),limit=500)
        export_changes_csv(path,rows)
        QMessageBox.information(self,'موفق' if fa else 'Success',
         'گزارش ذخیره شد.' if fa else 'Report exported.')
       except (OSError,PermissionError,ValueError,sqlite3.Error) as exc:
        QMessageBox.warning(self,'خطا' if fa else 'Error',str(exc))
      permission_history_button.clicked.connect(load_permission_history)
      export_permission_history_button.clicked.connect(export_permission_history)
      audit_buttons.addWidget(permission_history_button);audit_buttons.addWidget(export_permission_history_button)
      v.addLayout(audit_buttons)
      v.addWidget(QLabel('رویدادهای امنیتی بدون ثبت رمز عبور ذخیره می‌شوند.' if fa else
                         'Security events are recorded without storing passwords.'))
     elif i==16:
      w,v=self.page('گزارش مالی پیشرفته')
      if self.role=='admin':
       income=c.execute('SELECT COALESCE(SUM(amount),0) FROM payments').fetchone()[0]
       costs=c.execute('SELECT COALESCE(SUM(amount),0) FROM expenses').fetchone()[0]
       for label,amount in [('کل دریافت‌ها',income),('کل هزینه‌ها',costs),('خالص جریان نقدی ثبت‌شده',income-costs)]:
        card=QLabel(f'{label}  |  {self.format_money(amount)}');card.setObjectName('metric');v.addWidget(card)
       b=QPushButton('خروجی CSV گزارش مالی');b.setObjectName('primary');b.clicked.connect(self.financial_export);v.addWidget(b)
       v.addWidget(self.table(['ماه میلادی','دریافتی'],[(m,self.format_money(a)) for m,a in c.execute("SELECT substr(created_at,1,7),SUM(amount) FROM payments GROUP BY substr(created_at,1,7) ORDER BY 1 DESC LIMIT 12")]))
      else:v.addWidget(QLabel('دسترسی این صفحه مخصوص مدیر است.'))
     elif i==17:
      w,v=self.page('تحلیل اشغال هتل در بازه زمانی')
      controls=QHBoxLayout();start=QDateEdit();end=QDateEdit()
      for widget in (start,end):widget.setCalendarPopup(True);widget.setDisplayFormat('yyyy-MM-dd')
      start.setDate(QDate.currentDate());end.setDate(QDate.currentDate().addDays(13))
      controls.addWidget(QLabel('از تاریخ'));controls.addWidget(start);controls.addWidget(QLabel('تا تاریخ'));controls.addWidget(end);v.addLayout(controls)
      report=QTableWidget();v.addWidget(report)
      nonlocal_report=[report]
      def refresh_safe():
       first=start.date().toPython();last=end.date().toPython()
       if last<first or (last-first).days>365:QMessageBox.warning(self,'بازه نامعتبر','بازه را حداکثر ۳۶۶ روز انتخاب کنید.');return
       with connect() as db:
        total=db.execute("SELECT COUNT(*) FROM rooms WHERE status='فعال'").fetchone()[0]
        bookings=db.execute("SELECT room_id,checkin,checkout FROM reservations WHERE status IN ('رزرو شده','پذیرش شده') AND checkin<=? AND checkout>?",(last.isoformat(),first.isoformat())).fetchall()
       data=[];day=first
       while day<=last:
        key=day.isoformat();occupied=len({rid for rid,a,b in bookings if a<=key<b});percentage=round(occupied/total*100,1) if total else 0
        data.append((self.format_date(key),occupied,total,str(percentage)+'٪'));day+=timedelta(days=1)
       current=nonlocal_report[0];idx=v.indexOf(current);v.removeWidget(current);current.deleteLater();new=self.table(['تاریخ شمسی','اتاق رزروشده','اتاق فعال','درصد اشغال'],data);v.insertWidget(idx,new);nonlocal_report[0]=new
      button=QPushButton('محاسبه نرخ اشغال');button.setObjectName('primary');button.clicked.connect(refresh_safe);v.insertWidget(2,button);refresh_safe()
     elif i==18:
      w,v=self.page('گزارش رویدادهای امنیتی و مدیریتی')
      rows=c.execute('SELECT created_at,username,action,details FROM audit_log ORDER BY id DESC LIMIT 300').fetchall()
      v.addWidget(self.table(['زمان','کاربر','رویداد','جزئیات'],rows))
     elif i==19:
      w,v=self.page('مدیریت کدهای تخفیف')
      v.addWidget(QLabel('کدهای فعال را در بخش صورتحساب روی رزرو اعمال کنید.'))
      self.discount_code=QLineEdit();self.discount_code.setPlaceholderText('کد انگلیسی، مانند WELCOME10')
      self.discount_percent=QSpinBox();self.discount_percent.setRange(1,100);self.discount_percent.setSuffix('٪')
      bar=QHBoxLayout();bar.addWidget(self.discount_code);bar.addWidget(self.discount_percent)
      btn=QPushButton('ثبت کد');btn.setObjectName('primary');btn.clicked.connect(self.add_discount);bar.addWidget(btn);v.addLayout(bar)
      rows=c.execute('SELECT id,code,percent,active,created_at FROM discounts ORDER BY id DESC').fetchall()
      self.discount_table=self.table(['شناسه','کد','درصد','وضعیت','تاریخ'],[(rid,code,str(percent)+'٪','فعال' if active else 'غیرفعال',created) for rid,code,percent,active,created in rows]);v.addWidget(self.discount_table)
      toggle=QPushButton('تغییر وضعیت کد انتخاب‌شده');toggle.clicked.connect(self.toggle_discount);v.addWidget(toggle)
    # Keep large tables and forms usable on laptop-sized screens.
    scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(w)
    old=self.stack.widget(i);self.stack.removeWidget(old);old.deleteLater();self.stack.insertWidget(i,scroll);self.stack.setCurrentIndex(i);self._translate_page(scroll)
    for idx,button in enumerate(self.nav_buttons):button.setProperty('active',idx==i);button.style().unpolish(button);button.style().polish(button)
    if self.role=='admin' and self.user_id is not None:
     try:
      from security_notifications_v114 import unread_count
      from operation_guard import authorize_action
      with connect() as db:
       authorize_action(db,self.user_id,self.session_token,'security.view')
       alert_count=unread_count(db,self.user_id)
      self.security_sidebar_button.setText(('🔔  هشدارهای امنیتی' if self.language=='fa' else '🔔  Security alerts')+f' ({alert_count})')
     except (PermissionError,ValueError,sqlite3.Error,AttributeError):
      self.security_sidebar_button.setVisible(False)
    self.statusBar().showMessage(('Active section: ' if self.language=='en' else 'بخش فعال: ')+f'{self.nav_buttons[i].text().strip()} | Ashkan Hotel Pro v82.0')
 def add_order(self):
    if not self.authorize_operation('reservations.services'):return
    rid=self.order_res.currentData();mid=self.order_item.currentData()
    if rid is None or mid is None:QMessageBox.warning(self,'خطا','رزرو و خدمت معتبر انتخاب کنید.');return
    with connect() as c:
     row=c.execute('SELECT price FROM menu_items WHERE id=? AND active=1',(mid,)).fetchone()
     if not row:QMessageBox.warning(self,'خطا','خدمت یافت نشد.');return
     c.execute('INSERT INTO service_orders(reservation_id,item_id,quantity,unit_price) VALUES(?,?,?,?)',(rid,mid,self.order_qty.value(),row[0]))
    self.navigate(12)
 def add_inventory(self):
    if not self.authorize_operation('finance.inventory'):return
    if self.role!='admin':QMessageBox.warning(self,'دسترسی','این عملیات مخصوص مدیر است.');return
    name=self.inv_name.text().strip()
    if not name:QMessageBox.warning(self,'خطا','نام کالا ضروری است.');return
    with connect() as c:
     c.execute('INSERT INTO inventory(name,unit,quantity,minimum) VALUES(?,?,?,?) ON CONFLICT(name) DO UPDATE SET quantity=inventory.quantity+excluded.quantity,minimum=excluded.minimum',(name,self.inv_unit.currentText(),self.inv_qty.value(),self.inv_min.value()))
    self.navigate(13)
 def add_expense(self):
    if not self.authorize_operation('finance.expense'):return
    if self.role!='admin':QMessageBox.warning(self,'دسترسی','این عملیات مخصوص مدیر است.');return
    if not self.exp_description.text().strip() or self.exp_amount.value()<=0:QMessageBox.warning(self,'خطا','شرح و مبلغ معتبر وارد کنید.');return
    with connect() as c:c.execute('INSERT INTO expenses(category,description,amount) VALUES(?,?,?)',(self.exp_category.currentText(),self.exp_description.text().strip(),self.exp_amount.value()))
    audit(self.username,'add_expense',self.exp_description.text().strip());self.navigate(8)
 def add_employee(self):
    if not self.authorize_operation('staff.manage'):return
    if self.role!='admin':QMessageBox.warning(self,'دسترسی','این عملیات مخصوص مدیر است.');return
    errors=validate_employee(self.staff_name.text(),self.staff_phone.text(),self.staff_salary.value())
    if errors:QMessageBox.warning(self,'اعتبارسنجی کارمند','\n'.join(errors.values()));return
    with connect() as c:c.execute('INSERT INTO employees(full_name,position,phone,salary) VALUES(?,?,?,?)',(self.staff_name.text().strip(),self.staff_position.currentText(),self.staff_phone.text().strip(),self.staff_salary.value()))
    audit(self.username,'add_employee',self.staff_name.text().strip());self.navigate(9)
 def toggle_employee(self):
    if not self.authorize_operation('staff.manage'):return
    if self.role!='admin':QMessageBox.warning(self,'دسترسی','این عملیات مخصوص مدیر است.');return
    row=self.staff_table.currentRow()
    if row<0:return
    eid=int(self.staff_table.item(row,0).text())
    with connect() as c:c.execute('UPDATE employees SET active=1-active WHERE id=?',(eid,))
    self.navigate(9)
 def show_invoice(self):
    rid=self.invoice_res.currentData()
    if rid is None:QMessageBox.information(self,'صورتحساب','رزروی وجود ندارد.');return
    with connect() as c:
     authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
     inv=calculate_invoice(c,rid)
    dlg=QDialog(self);dlg.setWindowTitle(('Invoice #' if self.language=='en' else 'صورتحساب شماره ')+str(rid));dlg.resize(620,590);layout=QVBoxLayout(dlg)
    bar=QHBoxLayout();code=QLineEdit();code.setPlaceholderText('کد تخفیف (اختیاری)');tax=QSpinBox();tax.setRange(0,100);tax.setSuffix('٪ مالیات')
    code.setText(inv['code'] or '');tax.setValue(inv['tax_percent']);bar.addWidget(code);bar.addWidget(tax);layout.addLayout(bar)
    browser=QTextBrowser();layout.addWidget(browser)
    def refresh():
     with connect() as c:
      authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
      data=calculate_invoice(c,rid)
     fields=[('شماره رزرو',data['id']),('مهمان',data['guest']),('اتاق',data['room']),('ورود',self.format_date(data['start'])),('خروج',self.format_date(data['end'])),('شب اقامت',data['nights']),('اقامت',self.format_money(data['accommodation'])),('خدمات',self.format_money(data['services'])),('جمع اولیه',self.format_money(data['subtotal'])),('تخفیف',f"{data['discount_percent']}٪ / {self.format_money(data['discount'])}"),('مالیات',f"{data['tax_percent']}٪ / {self.format_money(data['tax'])}"),('مبلغ نهایی',self.format_money(data['total'])),('دریافتی',self.format_money(data['paid'])),('مانده',self.format_money(data['balance']))]
     body=''.join('<p><b>'+html.escape(str(k))+'</b>: '+html.escape(str(val))+'</p>' for k,val in fields)
     browser.setHtml(render_invoice(fields,self.language))
    def save():
     try:
      with connect() as c:
       authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
       apply_adjustment(c,rid,code.text(),tax.value())
      audit(self.username,'invoice_adjustment',str(rid));refresh()
      QMessageBox.information(dlg,'موفق','تخفیف و مالیات رزرو ذخیره شد.')
     except (PermissionError,ValueError,sqlite3.Error) as exc:QMessageBox.warning(dlg,'خطا',str(exc))
    button=QPushButton('Apply discount and tax' if self.language=='en' else 'اعمال تخفیف و مالیات');button.setObjectName('primary');button.clicked.connect(save);layout.addWidget(button)
    refresh();dlg.exec()
 def export_reservations(self):
    path,_=QFileDialog.getSaveFileName(self,'ذخیره CSV','hotel-reservations.csv','CSV (*.csv)')
    if not path:return
    with connect() as c:rows=branch_export_rows(c,self.user_id,self.role,self.active_branch)
    try:
     with open(path,'w',encoding='utf-8-sig',newline='') as f:
      writer=csv.writer(f);writer.writerow(['شناسه','اتاق','مهمان','ورود میلادی','خروج میلادی','وضعیت']);writer.writerows(rows)
     QMessageBox.information(self,'موفق','فایل CSV ذخیره شد.')
    except OSError as e:QMessageBox.critical(self,'خطا',str(e))
 def add_room(self):
    if self.role!='admin':QMessageBox.warning(self,translate('دسترسی',self.language),translate('فقط مدیر می‌تواند اتاق اضافه کند.',self.language));return
    num,ok=QInputDialog.getText(self,translate('اتاق جدید',self.language),translate('شماره اتاق:',self.language))
    if not ok or not num.strip():return
    kind,ok=QInputDialog.getItem(self,translate('نوع اتاق',self.language),translate('نوع:',self.language), [translate(k,self.language) for k in ['استاندارد','دلوکس','سوئیت','VIP']],0,False)
    if not ok:return
    kind=({'Standard':'استاندارد','Deluxe':'دلوکس','Suite':'سوئیت'}).get(kind,kind)
    rate,ok=QInputDialog.getInt(self,translate('نرخ شبانه',self.language),translate('مبلغ به تومان:',self.language),2000000,1,2000000000,100000)
    if not ok:return
    errors=validate_room(num,kind,rate)
    if errors:QMessageBox.warning(self,translate('اعتبارسنجی اتاق',self.language),'\n'.join(translate(message,self.language) for message in errors.values()));return
    try:
     with connect() as c:
      require_branch(c,self.user_id,self.role,self.active_branch)
      c.execute('INSERT INTO rooms(number,kind,rate,branch_id) VALUES(?,?,?,?)',(normalize_digits(num.strip()),kind,rate,self.active_branch))
     self.navigate(1)
    except (sqlite3.IntegrityError,PermissionError,ValueError) as exc:QMessageBox.warning(self,translate('خطا',self.language),str(exc))
 def add_housekeeping(self):
    with connect() as c:create_housekeeping(c,self.user_id,self.role,self.active_branch,self.house_room.currentData(),self.house_task.currentText())
    self.navigate(5)
 def finish_housekeeping(self):
    row=self.house_table.currentRow()
    if row<0:QMessageBox.information(self,'انتخاب','یک وظیفه را انتخاب کنید.');return
    task_id=int(self.house_table.item(row,0).text())
    with connect() as c:complete_housekeeping(c,self.user_id,self.role,self.active_branch,task_id)
    self.navigate(5)
 def backup(self):
    path,_=QFileDialog.getSaveFileName(self,'ذخیره پشتیبان','ashkan-hotel-backup.db','SQLite Database (*.db)')
    if not path:return
    try:
     with connect() as src,sqlite3.connect(path) as dst:src.backup(dst)
     QMessageBox.information(self,'موفق','پشتیبان ذخیره شد.')
    except sqlite3.Error as e:QMessageBox.critical(self,'خطا',str(e))
 def change_password(self):
    en=self.language=='en'
    dialog=QDialog(self)
    dialog.setWindowTitle('Change password' if en else 'تغییر رمز عبور')
    dialog.setMinimumWidth(440)
    layout=QVBoxLayout(dialog)
    heading=QLabel('Secure password update' if en else 'تغییر امن رمز عبور')
    heading.setObjectName('title');layout.addWidget(heading)
    form=QFormLayout();fields=[]
    labels=(('Current password','New password','Confirm new password') if en else ('رمز فعلی','رمز جدید','تکرار رمز جدید'))
    for label in labels:
     field=QLineEdit();field.setEchoMode(QLineEdit.EchoMode.Password)
     field.setMinimumHeight(38);form.addRow(label,field);fields.append(field)
    layout.addLayout(form)
    note=QLabel('Use 12+ characters with letters and numbers or symbols.' if en else 'حداقل ۱۲ نویسه شامل حروف و اعداد یا نمادها')
    note.setWordWrap(True);layout.addWidget(note)
    error=QLabel('');error.setWordWrap(True);error.setStyleSheet('color:#ff8c8c;');layout.addWidget(error)
    show=QPushButton('Show passwords' if en else 'نمایش رمزها');show.setCheckable(True)
    show.toggled.connect(lambda visible:[field.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password) for field in fields])
    layout.addWidget(show)
    buttons=QHBoxLayout();cancel=QPushButton('Cancel' if en else 'انصراف');save=QPushButton('Update password' if en else 'ثبت رمز جدید')
    save.setObjectName('primary');buttons.addWidget(cancel);buttons.addWidget(save);layout.addLayout(buttons)
    cancel.clicked.connect(dialog.reject)
    def submit():
     try:
      with connect() as c:rotate_password(c,self.username,fields[0].text(),fields[1].text(),fields[2].text())
      audit(self.username,'password_changed')
      dialog.accept()
      QMessageBox.information(self,'Success' if en else 'موفق','Password updated.' if en else 'رمز عبور با موفقیت تغییر کرد.')
     except (ValueError,sqlite3.Error) as exc:
      messages={'New passwords do not match.':'تکرار رمز با رمز جدید یکسان نیست.', 'Current password is incorrect.':'رمز فعلی نادرست است.', 'Password must contain at least 12 characters.':'رمز جدید باید حداقل ۱۲ نویسه باشد.', 'Password is too long.':'رمز بیش از حد طولانی است.', 'Password must not start or end with spaces.':'رمز نباید با فاصله شروع یا تمام شود.', 'Password must not contain your username.':'رمز نباید شامل نام کاربری باشد.', 'Use a combination of letters, digits or symbols.':'از ترکیب حروف و اعداد یا نمادها استفاده کنید.', 'New password must be different from the current password.':'رمز جدید باید با رمز فعلی متفاوت باشد.'}
      error.setText(str(exc) if en else messages.get(str(exc),'خطا در تغییر رمز عبور'))
    save.clicked.connect(submit)
    dialog.exec()
 def filter_reservations(self, query):
    selected=self.res_status_filter.currentData() if hasattr(self,'res_status_filter') else None
    for r in range(self.res_table.rowCount()):
     values=[self.res_table.item(r,col).text() if self.res_table.item(r,col) else '' for col in range(self.res_table.columnCount())]
     self.res_table.setRowHidden(r,not matches_reservation(values,query,selected,self.language))
 def add_discount(self):
    if not self.ensure_admin():return
    code=self.discount_code.text().strip().upper()
    if not code or len(code)>32 or not all(ch.isascii() and (ch.isalnum() or ch in '-_') for ch in code):
     QMessageBox.warning(self,'کد نامعتبر','کد تخفیف باید ۱ تا ۳۲ نویسه انگلیسی، عدد، خط تیره یا زیرخط باشد.');return
    try:
     with connect() as c:c.execute('INSERT INTO discounts(code,percent) VALUES(?,?)',(code,self.discount_percent.value()))
     audit(self.username,'create_discount',code);self.navigate(19)
    except sqlite3.IntegrityError:QMessageBox.warning(self,'تکراری','این کد قبلاً ثبت شده است.')
 def toggle_discount(self):
    if not self.ensure_admin():return
    row=self.discount_table.currentRow()
    if row<0:return
    discount_id=int(self.discount_table.item(row,0).text())
    with connect() as c:c.execute('UPDATE discounts SET active=1-active WHERE id=?',(discount_id,))
    audit(self.username,'toggle_discount',str(discount_id));self.navigate(19)
 def edit_booking(self):
    if not self.authorize_operation('reservations.update'):return
    row=self.res_table.currentRow()
    if row<0:QMessageBox.information(self,'انتخاب','یک رزرو را انتخاب کنید.');return
    rid=int(self.res_table.item(row,0).text())
    try:
     with connect() as c:
      authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
      record=c.execute('SELECT room_id,checkin,checkout,status FROM reservations WHERE id=?',(rid,)).fetchone()
      rooms=c.execute("SELECT id,number,kind FROM rooms WHERE status='فعال' AND branch_id=? ORDER BY number",(self.active_branch,)).fetchall()
    except (PermissionError,ValueError) as exc:
     QMessageBox.warning(self,'عدم دسترسی',str(exc));return
    if not record or record[3]!='رزرو شده':QMessageBox.warning(self,'محدودیت','فقط رزروهای پذیرش‌نشده قابل تغییر هستند.');return
    language=self.language
    dlg=QDialog(self)
    dlg.setWindowTitle(('ویرایش رزرو ' if language=='fa' else 'Edit reservation #')+str(rid))
    dlg.setMinimumWidth(500)
    dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language=='fa' else Qt.LayoutDirection.LeftToRight)
    form=QFormLayout(dlg);form.setSpacing(12)
    room=QComboBox()
    for room_id,num,kind in rooms:room.addItem(f'{num} - {kind}',room_id)
    index=room.findData(record[0]);room.setCurrentIndex(index)
    start=QDateEdit();end=QDateEdit()
    for widget,value in ((start,record[1]),(end,record[2])):
     widget.setCalendarPopup(True);widget.setDisplayFormat('yyyy-MM-dd')
     widget.setDate(QDate.fromString(value,'yyyy-MM-dd'));widget.setMinimumHeight(38)
    room.setMinimumHeight(38)
    form.addRow('اتاق' if language=='fa' else 'Room',room)
    form.addRow('ورود' if language=='fa' else 'Check-in',start)
    form.addRow('خروج' if language=='fa' else 'Check-out',end)
    validation=QLabel('');validation.setWordWrap(True)
    validation.setStyleSheet('color:#ef8f94;font-weight:600')
    form.addRow(validation)
    button=QPushButton('ثبت تغییرات' if language=='fa' else 'Save changes')
    button.setObjectName('primary');button.setMinimumHeight(40);form.addRow(button)
    def validate_edit():
     from reservation_edit_validation import validate_edit_dates, room_conflict
     selected=room.currentData()
     checkin=start.date().toString('yyyy-MM-dd')
     checkout=end.date().toString('yyyy-MM-dd')
     error=validate_edit_dates(checkin,checkout,selected,language)
     if not error:
      try:
       with connect() as db:
        authorize_reservation(db,self.user_id,self.role,self.active_branch,rid)
        require_room(db,self.user_id,self.role,self.active_branch,selected)
        conflict=db.execute("""SELECT 1 FROM reservations WHERE room_id=? AND id<>?
         AND status IN ('رزرو شده','پذیرش شده') AND checkin<? AND checkout>? LIMIT 1""",
         (selected,rid,checkout,checkin)).fetchone()
       if room_conflict(bool(conflict)):
        error='تداخل زمانی با رزرو دیگر' if language=='fa' else 'Room is booked during these dates.'
      except (PermissionError,ValueError,sqlite3.Error) as exc:
       error=str(exc)
     validation.setText(error)
     for widget in (start,end,room):
      widget.setProperty('invalid',bool(error))
      widget.style().unpolish(widget);widget.style().polish(widget)
     button.setEnabled(not bool(error))
     return not error
    start.dateChanged.connect(lambda _:validate_edit())
    end.dateChanged.connect(lambda _:validate_edit())
    room.currentIndexChanged.connect(lambda _:validate_edit())
    def save():
     if not validate_edit():return
     try:
      with connect() as c:
       authorize_reservation(c,self.user_id,self.role,self.active_branch,rid)
       require_room(c,self.user_id,self.role,self.active_branch,room.currentData())
       amount=reschedule(c,rid,room.currentData(),start.date().toString('yyyy-MM-dd'),end.date().toString('yyyy-MM-dd'))
      audit(self.username,'reschedule',f'{rid}: {amount}');dlg.accept();self.navigate(2)
     except (PermissionError,ValueError,sqlite3.Error) as exc:
      validation.setText(str(exc));button.setEnabled(False)
    button.clicked.connect(save)
    validate_edit()
    dlg.exec()
 def add_booking(self):
    if not self.authorize_operation('reservations.create'):return
    if BookingDialog(self).exec():self.navigate(2)
 def change_status(self,status):
    if not self.authorize_operation('reservations.update'):return
    row=self.res_table.currentRow()
    if row<0:QMessageBox.information(self,'انتخاب','ابتدا یک رزرو را انتخاب کنید.');return
    rid=int(self.res_table.item(row,0).text())
    with connect() as c:
     try:change_reservation_status(c,self.user_id,self.role,self.active_branch,rid,status)
     except (PermissionError,ValueError) as exc:QMessageBox.warning(self,'وضعیت نامعتبر',str(exc));return
    audit(self.username,'reservation_status',str(rid)+' -> '+status);self.navigate(2)
 def _validate_payment_form(self):
    errors=validate_payment(self.payment_res.currentData(),self.amount.value(),self.method.currentData())
    message='\n'.join(translate(msg,self.language) for msg in errors.values())
    self.payment_error.setText(message)
    self.payment_error.setVisible(bool(message))
    for widget,key in ((self.payment_res,'reservation'),(self.amount,'amount'),(self.method,'method')):
     widget.setProperty('invalid',key in errors)
     widget.style().unpolish(widget);widget.style().polish(widget)
    return not errors
 def pay(self):
    if not self.authorize_operation('reservations.payment'):return
    rid=self.payment_res.currentData()
    errors=validate_payment(rid,self.amount.value(),self.method.currentData())
    if errors:
     self._validate_payment_form()
     return
    try:
     with connect() as c:record_payment(c,self.user_id,self.role,self.active_branch,rid,self.amount.value(),self.method.currentData())
    except (PermissionError,ValueError) as exc:QMessageBox.warning(self,translate('عدم دسترسی',self.language),str(exc));return
    audit(self.username,'payment',str(rid)+' / '+str(self.amount.value()));self.navigate(4)
def _revoke_on_exit(token):
 from security_sessions import revoke_session
 try:
  with connect() as db:revoke_session(db,token)
 except sqlite3.Error:
  pass

if __name__=='__main__':
 init();app=QApplication(sys.argv);app.setLayoutDirection(Qt.LayoutDirection.RightToLeft);app.setStyleSheet(STYLE)
 from first_run_security import needs_admin_setup
 from first_run_dialog import FirstRunDialog
 with connect() as conn: setup_needed=needs_admin_setup(conn)
 if setup_needed and FirstRunDialog(connect).exec()!=QDialog.DialogCode.Accepted:sys.exit(0)
 login=LoginDialog();app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if login.language=='fa' else Qt.LayoutDirection.LeftToRight);
 if login.exec()!=QDialog.DialogCode.Accepted:sys.exit(0)
 from security_sessions import create_session
 with connect() as db:session_token=create_session(db,login.user_id)
 window=Main(login.role,login.user_id,login.username_value);window.session_token=session_token
 window.start_security_monitor()
 app.aboutToQuit.connect(lambda: _revoke_on_exit(session_token))
 window.show();sys.exit(app.exec())

