"""Presentation-safe, indicative accommodation KPIs for executive dashboards."""
from datetime import date,timedelta

def report_window(today, days):
    if days not in (7,30,90): raise ValueError('Unsupported period')
    end=date.fromisoformat(today)+timedelta(days=1)
    return (end-timedelta(days=days)).isoformat(),end.isoformat()

def dashboard_kpis(performance):
    capacity=performance['available_room_nights']
    occupied=performance['occupied_room_nights']
    missing=performance['missing_quotes']
    if capacity<0 or occupied<0: raise ValueError('Negative room nights')
    return {
      'occupancy_percent': round(100*occupied/capacity,1) if capacity else None,
      'estimated_adr': performance['estimated_adr'],
      'estimated_revpar': performance['estimated_revpar'],
      'estimated_value': performance['estimated_accommodation_value'],
      'missing_quotes': missing,
      'overcapacity': occupied>capacity,
      'incomplete': bool(missing),
    }

def dashboard_alerts(kpis,language='fa'):
    if language not in ('fa','en'): raise ValueError('Unsupported language')
    fa=language=='fa'; alerts=[]
    if kpis['overcapacity']:alerts.append('اشغال بیش از ظرفیت محاسبه‌شده؛ داده‌ها را بررسی کنید.' if fa else 'Occupied nights exceed calculated capacity; review data.')
    if kpis['incomplete']:alerts.append('برخی رزروها نرخ ثبت‌شده ندارند؛ ADR و RevPAR قابل اتکا نیستند.' if fa else 'Some bookings lack quotes; ADR and RevPAR are unavailable.')
    if kpis['occupancy_percent'] is None:alerts.append('اتاق فعال برای این بازه وجود ندارد.' if fa else 'No active rooms in this reporting window.')
    elif kpis['occupancy_percent']<35:alerts.append('اشغال پایین‌تر از ۳۵٪ است.' if fa else 'Occupancy is below 35%.')
    return alerts
