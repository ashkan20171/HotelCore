"""Date conversion at the reporting boundary; SQL storage remains Gregorian."""
from datetime import date
import re

_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')

def normalize_report_date(value, language='fa'):
    """Return ISO Gregorian date from a Jalali (fa) or Gregorian (en) date."""
    value = str(value).strip().translate(_DIGITS).replace('/', '-')
    if not re.fullmatch(r'\d{4}-\d{1,2}-\d{1,2}', value):
        raise ValueError('Date must be YYYY-MM-DD')
    y, m, d = map(int, value.split('-'))
    if language == 'fa':
        import jdatetime
        return jdatetime.date(y, m, d).togregorian().isoformat()
    return date(y, m, d).isoformat()

def report_date(value, language='fa'):
    parsed = date.fromisoformat(value)
    if language == 'fa':
        import jdatetime
        return jdatetime.date.fromgregorian(date=parsed).strftime('%Y-%m-%d')
    return parsed.isoformat()
