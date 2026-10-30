"""Pure input validation for hotel reservations (no Qt/database dependency)."""
from datetime import date
import re

def validate_booking(name, phone, room_id, checkin, checkout):
    errors = {}
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 100:
        errors['name'] = 'نام مهمان باید حداقل دو نویسه باشد.'
    normalized_phone = str(phone or '').translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')).strip()
    digits = re.sub(r'[\s()+-]', '', normalized_phone)
    if not re.fullmatch(r'[0-9]{7,15}', digits):
        errors['phone'] = 'شماره تماس باید بین ۷ تا ۱۵ رقم داشته باشد.'
    if isinstance(room_id, bool) or not isinstance(room_id, int) or room_id <= 0:
        errors['room'] = 'اتاق معتبری انتخاب نشده است.'
    try:
        start, end = date.fromisoformat(checkin), date.fromisoformat(checkout)
        if end <= start:
            errors['dates'] = 'تاریخ خروج باید بعد از تاریخ ورود باشد.'
    except (ValueError, TypeError):
        errors['dates'] = 'تاریخ ورود یا خروج معتبر نیست.'
    return errors
