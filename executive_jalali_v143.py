"""Gregorian/solar-Hijri conversions for executive reporting controls."""
from datetime import date
import re

def jalali_label(day):
    import jdatetime
    if not isinstance(day,date):raise ValueError('Expected date')
    return jdatetime.date.fromgregorian(date=day).strftime('%Y/%m/%d')

def parse_jalali(value):
    import jdatetime
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{4}/[0-9]{2}/[0-9]{2}',value):
        raise ValueError('Use YYYY/MM/DD Jalali date')
    y,m,d=map(int,value.split('/'))
    if not 1200<=y<=1600:raise ValueError('Jalali year out of range')
    try:return jdatetime.date(y,m,d).togregorian()
    except (ValueError,OverflowError) as exc:raise ValueError('Invalid Jalali date') from exc
