"""Pure, locale-aware dashboard insights. No UI or database dependency."""
from decimal import Decimal


def revenue_change(monthly):
    """Percentage change between last two months; None if not comparable."""
    if len(monthly) < 2:
        return None
    old, new = monthly[-2][1], monthly[-1][1]
    if any(isinstance(x, bool) or not isinstance(x, (int, float, Decimal)) or x < 0 for x in (old, new)):
        raise ValueError('Revenue values must be nonnegative numbers')
    if old == 0:
        return None
    return round(float((new - old) / old * 100), 1)


def occupancy_message(rate, language='fa'):
    if not 0 <= rate <= 100:
        raise ValueError('Occupancy must be between 0 and 100')
    if rate >= 85:
        return 'High occupancy — plan room availability carefully' if language == 'en' else 'اشغال بالا — ظرفیت اتاق‌ها را با دقت مدیریت کنید'
    if rate >= 50:
        return 'Healthy occupancy — monitor upcoming check-outs' if language == 'en' else 'اشغال مناسب — خروج‌های پیش‌رو را بررسی کنید'
    return 'Low occupancy — consider promotions' if language == 'en' else 'اشغال پایین — پیشنهادهای ویژه را بررسی کنید'


def revenue_message(change, language='fa'):
    if change is None:
        return 'Not enough monthly data' if language == 'en' else 'داده ماهانه کافی نیست'
    sign = '+' if change > 0 else ''
    return (f'Month-over-month revenue: {sign}{change:.1f}%' if language == 'en'
            else f'تغییر دریافتی نسبت به ماه قبل: {sign}{change:.1f}٪')
