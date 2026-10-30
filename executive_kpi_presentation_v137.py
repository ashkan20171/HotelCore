"""Pure presentation rules for executive KPI comparisons and adaptive layouts."""
from math import isfinite

def responsive_columns(width):
    if not isinstance(width,(int,float)) or not isfinite(width):
        raise ValueError('Invalid viewport width')
    return 1 if width < 650 else 2 if width < 900 else 3

def compare_periods(current,previous):
    """Percent change vs prior period; zero denominator is intentionally undefined."""
    if isinstance(current,bool) or isinstance(previous,bool) or not isinstance(current,(int,float)) or not isinstance(previous,(int,float)):
        return {'kind':'unavailable','percent':None}
    if not isfinite(current) or not isfinite(previous):
        return {'kind':'unavailable','percent':None}
    if previous==0:
        return {'kind':'unchanged','percent':0.0} if current==0 else {'kind':'undefined','percent':None}
    pct=round((current-previous)/abs(previous)*100,1)
    return {'kind':'unchanged' if pct==0 else 'change','percent':pct}
