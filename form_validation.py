"""Pure input validation for Persian hotel management forms."""
import re
import unicodedata

_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_digits(value):
    return str(value).translate(_TRANSLATION)

def normalize_text(value):
    return unicodedata.normalize("NFKC", str(value or "")).strip()

def validate_room(number, kind, rate):
    errors = {}
    number = normalize_digits(normalize_text(number))
    if not number or len(number) > 16 or not re.fullmatch(r"[A-Za-z0-9\-]+", number):
        errors["number"] = "شماره اتاق باید ۱ تا ۱۶ نویسه شامل اعداد، حروف انگلیسی یا خط تیره باشد."
    if not normalize_text(kind):
        errors["kind"] = "نوع اتاق ضروری است."
    if not isinstance(rate, int) or isinstance(rate, bool) or not 0 < rate <= 2_000_000_000:
        errors["rate"] = "نرخ شبانه باید مبلغی مثبت و معتبر باشد."
    return errors

def validate_employee(name, phone, salary):
    errors = {}
    name = normalize_text(name)
    digits = normalize_digits(normalize_text(phone)).replace(" ", "").replace("-", "")
    if len(name) < 2 or len(name) > 100:
        errors["name"] = "نام کارمند باید بین ۲ تا ۱۰۰ نویسه باشد."
    if not re.fullmatch(r"\+?[0-9]{7,15}", digits):
        errors["phone"] = "شماره تماس باید ۷ تا ۱۵ رقم داشته باشد."
    if not isinstance(salary, int) or isinstance(salary, bool) or not 0 <= salary <= 2_000_000_000:
        errors["salary"] = "حقوق واردشده معتبر نیست."
    return errors

def validate_payment(reservation_id, amount, method):
    errors = {}
    if not isinstance(reservation_id, int) or isinstance(reservation_id, bool) or reservation_id <= 0:
        errors["reservation"] = "رزرو معتبر انتخاب کنید."
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        errors["amount"] = "مبلغ پرداخت باید بیشتر از صفر باشد."
    if normalize_text(method) not in {"نقدی", "کارتخوان", "انتقال بانکی"}:
        errors["method"] = "روش پرداخت معتبر انتخاب کنید."
    return errors
