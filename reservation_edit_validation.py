"""Pure validation helpers for the reservation edit dialog."""
from datetime import date

def validate_edit_dates(checkin, checkout, room_id, language='fa'):
    english = language == 'en'
    if isinstance(room_id, bool) or not isinstance(room_id, int) or room_id <= 0:
        return 'Select a valid room.' if english else 'یک اتاق معتبر انتخاب کنید.'
    try:
        first, last = date.fromisoformat(checkin), date.fromisoformat(checkout)
    except (TypeError, ValueError):
        return 'Enter valid dates.' if english else 'تاریخ معتبر وارد کنید.'
    if last <= first:
        return 'Check-out must be after check-in.' if english else 'تاریخ خروج باید بعد از ورود باشد.'
    return ''

def room_conflict(has_overlap):
    return bool(has_overlap)
