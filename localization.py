"""Presentation-only Persian/English translations. Never translate persisted DB values."""
import re

NAV_FA = ['داشبورد', 'اتاق\u200cها', 'رزروها', 'مهمانان', 'پرداخت\u200cها', 'خانه\u200cداری', 'گزارش\u200cها', 'تنظیمات', 'هزینه\u200cها', 'کارکنان', 'صورتحساب', 'تقویم رزرو', 'رستوران و خدمات', 'انبار', 'تحلیل درآمد', 'مدیریت کاربران', 'گزارش مالی پیشرفته', 'گزارش اشغال', 'گزارش رویدادها', 'تخفیف\u200cها', 'نقشه اشغال اتاق\u200cها', 'نرخ\u200cهای فصلی', 'اعلان\u200cهای پذیرش', 'مدیریت شعب', 'گزارش شعب', 'دسترسی کاربران به شعب']
NAV_EN = ['Dashboard', 'Rooms', 'Reservations', 'Guests', 'Payments', 'Housekeeping', 'Reports', 'Settings', 'Expenses', 'Employees', 'Invoices', 'Booking calendar', 'Restaurant & services', 'Inventory', 'Revenue analytics', 'User management', 'Advanced finance', 'Occupancy report', 'Audit log', 'Discounts', 'Occupancy map', 'Seasonal pricing', 'Front desk alerts', 'Branch management', 'Branch reports', 'Branch user access']
STRINGS = dict(zip(NAV_FA, NAV_EN))
STRINGS.update({'انتخاب شعبه': 'Select branch', 'کاربر': 'User', 'شعبه': 'Branch', 'اعطای دسترسی': 'Grant access', 'لغو دسترسی': 'Revoke access', 'نام مهمان': 'Guest name', 'شماره تماس': 'Phone', 'کد ملی (اختیاری)': 'National ID (optional)', 'اتاق': 'Room', 'ورود (میلادی)': 'Check-in (Gregorian)', 'خروج (میلادی)': 'Check-out (Gregorian)', 'ثبت رزرو': 'Create reservation', 'رزرو جدید': 'New reservation', 'نام کاربری': 'Username', 'رمز عبور': 'Password', 'ورود': 'Sign in', 'ورود امن | Ashkan Hotel Pro': 'Secure sign in | Ashkan Hotel Pro', '✦ ورود به پنل مدیریت هتل': '✦ Hotel management sign in', 'جست\u200cوجوی زنده در تمام ستون\u200cها…': 'Search all columns…', 'جست\u200cوجوی زنده در جدول': 'Live table search', 'همه': 'All', 'استاندارد': 'Standard', 'سوئیت': 'Suite', 'کارتخوان': 'Card', 'نقدی': 'Cash', 'انتقال بانکی': 'Bank transfer', 'نظافت روزانه': 'Daily cleaning', 'نظافت پس از خروج': 'Checkout cleaning', 'بازرسی': 'Inspection', 'تعمیر و نگهداری': 'Maintenance', 'حقوق و دستمزد': 'Payroll', 'تعمیرات': 'Repairs', 'مواد مصرفی': 'Supplies', 'آب و برق و گاز': 'Utilities', 'بازاریابی': 'Marketing', 'سایر': 'Other', 'پذیرش': 'Reception', 'مدیریت': 'Management', 'حسابداری': 'Accounting', 'نگهداری': 'Maintenance', 'رستوران': 'Restaurant', 'عدد': 'Item', 'کیلوگرم': 'Kilogram', 'لیتر': 'Litre', 'بسته': 'Pack', 'نام و نام خانوادگی': 'Full name', 'نام کالا': 'Item name', 'تاریخ': 'Date', 'مبلغ': 'Amount', 'شرح': 'Description', 'وضعیت': 'Status', 'نوع': 'Type', 'شماره': 'Number', 'نام': 'Name', 'تلفن': 'Phone', 'ظرفیت': 'Capacity', 'قیمت': 'Price', 'تعداد': 'Quantity', 'عملیات': 'Actions', 'فعال': 'Active', 'غیرفعال': 'Inactive', 'ثبت': 'Save', 'حذف': 'Delete', 'ویرایش': 'Edit', 'افزودن': 'Add', 'جست\u200cوجو': 'Search', 'خروج': 'Exit', 'دریافت': 'Receipt', 'پرداخت': 'Payment', 'ثبت پرداخت': 'Record payment', 'ثبت اتاق': 'Add room', 'ثبت مهمان': 'Add guest', 'ذخیره': 'Save', 'بستن': 'Close', 'بازگشت': 'Back', 'خالی': 'Vacant', 'رزرو شده': 'Reserved', 'اشغال': 'Occupied', 'موفق': 'Success', 'خطا': 'Error', 'عدم دسترسی': 'Access denied', 'نمایش': 'Showing', 'از': 'of'})

STRINGS.update({'مدیریت دسترسی کاربران به شعب': 'Branch user access management', 'داشبورد تحلیلی شعب': 'Branch analytics dashboard', 'نمایش گزارش': 'View report', 'گزارش مستقل هر شعبه بر اساس اتاق و رزرو؛ دریافتی فقط پرداخت\u200cهای ثبت\u200cشده است.': 'Independent branch report for rooms and reservations; receipts include recorded payments only.', 'بخش فعال: ': 'Active section: ', 'شناسه': 'ID', 'کد': 'Code', 'درصد': 'Percent', 'مهمان': 'Guest', 'شب اقامت': 'Nights', 'نرخ شبانه': 'Nightly rate', 'تاریخ ورود': 'Check-in date', 'تاریخ خروج': 'Check-out date', 'شماره اتاق': 'Room number', 'شماره رزرو': 'Reservation ID', 'ثبت تغییرات': 'Save changes', 'انتخاب': 'Select', 'تغییر وضعیت کد انتخاب\u200cشده': 'Toggle selected code status', 'مدیریت کدهای تخفیف': 'Discount code management', 'ثبت کد': 'Create code', 'کدهای فعال را در بخش صورتحساب روی رزرو اعمال کنید.': 'Apply active codes to reservations in the invoice section.', 'رزرو و خدمت معتبر انتخاب کنید.': 'Select a valid reservation and service.', 'دسترسی': 'Access', 'مبلغ نهایی': 'Grand total', 'مانده': 'Balance', 'جمع اولیه': 'Subtotal', 'مالیات': 'Tax', 'تخفیف': 'Discount', 'دریافتی': 'Received', 'اقامت': 'Accommodation', 'خدمات': 'Services', 'جست\u200cوجوی زنده در تمام ستون\u200cها…': 'Search all columns…'})


# Shared interface vocabulary used by the booking workflow and common dialogs.
STRINGS.update({
    'رزرو جدید': 'New reservation',
    'تاریخ ورود باید قبل از تاریخ خروج باشد.': 'Check-in must be before check-out.',
    'نام مهمان الزامی است.': 'Guest name is required.',
    'شماره تماس الزامی است.': 'Phone number is required.',
    'لطفاً اتاق را انتخاب کنید.': 'Please select a room.',
    'رزرو با موفقیت ثبت شد': 'Reservation created successfully',
    'تغییر رمز عبور': 'Change password',
    'رمز فعلی': 'Current password',
    'رمز جدید': 'New password',
    'تکرار رمز جدید': 'Confirm new password',
    'نمایش رمز': 'Show password',
    'مخفی کردن رمز': 'Hide password',
    'انصراف': 'Cancel',
    'تأیید': 'Confirm',
    'روز': 'Day',
    'ماه': 'Month',
    'سال': 'Year',
    'امروز': 'Today',
})

# Room and payment workflow strings; values in SQLite remain canonical.
STRINGS.update({
 'اتاق جدید':'New room', 'شماره اتاق:':'Room number:', 'نوع اتاق':'Room type',
 'نوع:':'Type:', 'نرخ شبانه':'Nightly rate', 'مبلغ به تومان:':'Amount (toman):',
 'اعتبارسنجی اتاق':'Room validation', 'اعتبارسنجی پرداخت':'Payment validation',
 'فقط مدیر می‌تواند اتاق اضافه کند.':'Only administrators can add rooms.',
 'دسترسی':'Access', 'عدم دسترسی':'Access denied', 'تکراری':'Duplicate',
 'اتاق با این شماره قبلاً ثبت شده است.':'A room with this number already exists.',
 'خطا':'Error', 'موفق':'Success', 'انتخاب':'Selection',
 'پرداخت ثبت شد.':'Payment recorded.', 'نامعتبر':'Invalid',
 'استاندارد':'Standard', 'دلوکس':'Deluxe', 'سوئیت':'Suite',
 'کارتخوان':'Card terminal', 'نقدی':'Cash', 'انتقال بانکی':'Bank transfer',
})

def localize_errors(errors, language='fa'):
    """Translate validation messages without altering validation keys."""
    if isinstance(errors, dict):
        return {key: translate(str(value), language) for key, value in errors.items()}
    return [translate(str(value), language) for value in errors]

def translate(text, language='fa'):
    if language != 'en' or not text:
        return text
    if text in STRINGS:
        return STRINGS[text]
    if text.startswith('◈  '):
        return '◈  ' + translate(text[3:], language)
    if text.startswith('✦ ') and text[2:] in STRINGS:
        return '✦ ' + translate(text[2:], language)
    # Replace whole Persian phrases only, not substrings inside DB records.
    if text.startswith('مدیریت هتل • نسخه '):
        return text.replace('مدیریت هتل • نسخه ', 'Hotel management • v')
    if text.startswith('آماده | اطلاعات در پایگاه داده محلی SQLite ذخیره می‌شود'):
        return 'Ready | Data is stored in local SQLite database'
    if text.startswith('شعبه فعال: '):
        return 'Active branch: ' + text[len('شعبه فعال: '):]
    return text

def is_rtl(language):
    return language == 'fa'

# Version 37: guest and payment module vocabulary.
STRINGS.update({'تعداد مهمانان':'Guest count','فهرست مهمانان':'Guest list','کد ملی':'National ID','رزرو':'Reservation','روش پرداخت':'Payment method','روش':'Method','زمان':'Time','ثبت دریافت':'Record payment'})

# Version 68: polished interface vocabulary for every major workflow.
STRINGS.update({
 'داشبورد مدیریت هتل':'Hotel Management Dashboard', 'رزرو جدید':'New reservation',
 'اتاق‌های هتل':'Hotel Rooms', 'اتاق جدید':'New room', 'افزودن اتاق':'Add Room',
 'وضعیت اتاق':'Room Status', 'اتاق‌های خالی':'Available Rooms', 'اتاق‌های رزروشده':'Reserved Rooms',
 'مهمانان':'Guests', 'فهرست مهمانان':'Guest Directory', 'ثبت مهمان':'Add Guest',
 'پرداخت‌ها':'Payments', 'ثبت دریافت':'Record Payment', 'خانه‌داری':'Housekeeping',
 'کارهای خانه‌داری':'Housekeeping Tasks', 'گزارش‌ها':'Reports', 'تنظیمات':'Settings',
 'تنظیمات زبان':'Language Settings', 'زبان رابط کاربری':'Interface Language',
 'فارسی':'Persian', 'English':'English', 'هزینه‌ها':'Expenses', 'ثبت هزینه':'Record Expense',
 'کارکنان':'Employees', 'افزودن کارمند':'Add Employee', 'صورتحساب':'Invoices',
 'تقویم رزرو':'Booking Calendar', 'رستوران و خدمات':'Restaurant & Services',
 'ثبت سفارش و افزودن به صورتحساب':'Create Order & Add to Invoice', 'مدیریت موجودی و هشدار کمبود':'Inventory & Low-stock Alerts',
 'تحلیل مالی و عملکرد':'Financial & Performance Analytics', 'مدیریت کاربران و نقش‌ها':'Users & Roles',
 'گزارش مالی پیشرفته':'Advanced Financial Report', 'تحلیل اشغال هتل در بازه زمانی':'Hotel Occupancy Analysis',
 'گزارش رویدادهای امنیتی و مدیریتی':'Security & Management Audit Log',
 'مدیریت کدهای تخفیف':'Discount Code Management', 'نقشه اشغال اتاق‌ها':'Room Occupancy Map',
 'نرخ‌های فصلی':'Seasonal Rates', 'اعلان‌های پذیرش':'Front Desk Alerts',
 'مدیریت شعب':'Branch Management', 'داشبورد تحلیلی شعب':'Branch Analytics Dashboard',
 'مدیریت دسترسی کاربران به شعب':'Branch Access Management', 'انتخاب شعبه فعال':'Select Active Branch',
 'انتخاب شعبه':'Select Branch', 'نام مهمان':'Guest Name', 'شماره تماس':'Phone Number',
 'کد ملی (اختیاری)':'National ID (Optional)', 'ورود (میلادی)':'Check-in (Gregorian)',
 'خروج (میلادی)':'Check-out (Gregorian)', 'ثبت رزرو':'Create Reservation',
 'نمایش صورتحساب':'View Invoice', 'ذخیره PDF':'Save PDF', 'اعمال تخفیف و مالیات':'Apply Discount & Tax',
 'نام کالا':'Item Name', 'موجودی اولیه / مقدار افزایش':'Initial Stock / Quantity to Add',
 'حداقل موجودی':'Minimum Stock', 'ثبت کالا / افزایش موجودی':'Save Item / Increase Stock',
 'کد انگلیسی، مانند WELCOME10':'Code, e.g. WELCOME10', 'تغییر وضعیت کد انتخاب‌شده':'Toggle Selected Code',
 'خروجی CSV گزارش مالی':'Export Financial CSV', 'محاسبه نرخ اشغال':'Calculate Occupancy',
 'از تاریخ':'From Date', 'تا تاریخ':'To Date', 'گزارش دریافتی':'Payment Report',
 'گزارش مدیریتی PDF':'Management PDF Report', 'ثبت هزینه شعبه':'Record Branch Expense',
 'دسته هزینه':'Expense Category', 'شرح (اختیاری)':'Description (Optional)',
 'مبلغ (تومان)':'Amount (Toman)', 'مقایسه گردش وجوه شعب':'Compare Branch Cash Flow',
 'مقایسه با دوره قبل':'Compare with Previous Period', 'نمایش روند ماهانه':'Show Monthly Trend',
 'نمایش روند شعب':'Show Branch Trends', 'خروجی Excel روند ماهانه':'Export Monthly Trend to Excel',
 'خروجی Excel فیلترشده':'Export Filtered Excel', 'خروجی CSV مقایسه شعب':'Export Branch Comparison CSV',
 'خروجی PDF مقایسه شعب':'Export Branch Comparison PDF', 'مقایسه تصویری شعب':'Visual Branch Comparison',
 'روند ماهانه شعب مجاز':'Monthly Trend for Authorized Branches',
 'تمام شعب قابل مشاهده':'All Visible Branches', 'نمایش گزارش':'View Report',
 'نام کاربری':'Username', 'رمز عبور':'Password', 'تغییر رمز عبور':'Change Password',
 'رمز فعلی':'Current Password', 'رمز جدید':'New Password', 'تکرار رمز جدید':'Confirm New Password',
 'ایجاد کاربر':'Create User', 'دسترسی این صفحه مخصوص مدیر است.':'This page is restricted to administrators.',
 'این بخش فقط برای مدیر مجاز است.':'This section is available to administrators only.',
 'بازه نامعتبر':'Invalid Date Range', 'بازه را حداکثر ۳۶۶ روز انتخاب کنید.':'Select a range of no more than 366 days.',
 'رزرو و خدمت معتبر انتخاب کنید.':'Select a valid reservation and service.',
 'خدمت یافت نشد.':'Service not found.', 'نام کالا ضروری است.':'Item name is required.',
 'شرح و مبلغ معتبر وارد کنید.':'Enter a valid description and amount.',
 'ابتدا یک رزرو را انتخاب کنید.':'Select a reservation first.',
 'گزارش ذخیره شد.':'Report saved successfully.', 'هزینه ثبت شد.':'Expense saved successfully.',
 'صورتحساب PDF ذخیره شد.':'Invoice PDF saved successfully.',
 'تخفیف و مالیات رزرو ذخیره شد.':'Reservation discount and tax saved.',
 'اطلاعات در پایگاه داده محلی SQLite ذخیره می‌شود':'Data is stored in the local SQLite database',
 'آماده':'Ready', 'تاریخ شمسی':'Jalali Date', 'اتاق رزروشده':'Reserved Rooms',
 'اتاق فعال':'Active Rooms', 'درصد اشغال':'Occupancy Rate', 'کالا':'Item', 'واحد':'Unit',
 'موجودی':'Stock', 'وضعیت':'Status', 'دریافتی ثبت‌شده':'Recorded Receipts',
 'هزینه‌های ثبت‌شده':'Recorded Expenses', 'خالص جریان نقدی ساده (دریافتی منهای هزینه)':'Net Cash Flow (Receipts minus Expenses)',
 'خدمات سفارش‌داده‌شده (نه لزوماً وصول‌شده)':'Ordered Services (not necessarily collected)',
 'کاربر':'User', 'رویداد':'Event', 'جزئیات':'Details', 'زمان':'Time', 'روش پرداخت':'Payment method',
 'تعداد مهمانان':'Guest count', 'فهرست مهمانان':'Guest Directory', 'ثبت پرداخت':'Record Payment',
})
# Keep the navigation labels byte-for-byte aligned with the established UI glossary.
STRINGS.update(dict(zip(NAV_FA, NAV_EN)))
