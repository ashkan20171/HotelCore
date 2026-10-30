"""Presentation-only locale formatting; never mutate persisted database values."""
from datetime import date, datetime
try:
    import jdatetime
except ImportError:
    jdatetime = None


def display_date(value, language='fa'):
    """Convert an ISO Gregorian date to a localized display string."""
    if value is None:
        return ''
    if isinstance(value, (date, datetime)):
        value = value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    value = str(value)
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return value
    if language == 'en':
        return parsed.isoformat()
    if jdatetime is None:
        raise RuntimeError('jdatetime is required for Persian dates; install requirements.txt')
    return jdatetime.date.fromgregorian(date=parsed).strftime('%Y/%m/%d')


def display_money(value, language='fa'):
    """Use the existing toman amounts in both languages, without false FX conversion."""
    amount = int(value)
    return f'{amount:,} ' + ('toman' if language == 'en' else 'تومان')
