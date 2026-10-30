"""Pure KPI comparison and review signals for security analytics."""
from datetime import datetime, timedelta, timezone
from security_chart_v111 import chart_data

def compare_windows(conn, actor_id, *, days=7, username=None, now=None, alert_threshold=5):
    if type(days) is not int or not 1 <= days <= 90: raise ValueError('Invalid date range')
    if type(alert_threshold) is not int or not 1 <= alert_threshold <= 100: raise ValueError('Invalid alert threshold')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError('Timezone-aware date required')
    current=chart_data(conn,actor_id,days=days,username=username,now=now)
    previous=chart_data(conn,actor_id,days=days,username=username,now=now-timedelta(days=days))
    def count(chart):return chart['totals']['failure']+chart['totals']['locked']
    current_bad=count(current); previous_bad=count(previous)
    difference=current_bad-previous_bad
    severity='high' if current_bad>=alert_threshold and difference>0 else ('review' if current_bad>=alert_threshold else 'normal')
    return {'current':current,'previous':previous,'failed_delta':difference,
            'failed_delta_pct':round(100*difference/previous_bad,1) if previous_bad else None,
            'alert':severity,'threshold':alert_threshold}

def kpi_labels(result,fa=True):
    current=result['current']; previous=result['previous']
    return [
        ('ورود موفق' if fa else 'Successful logins',current['totals']['success']),
        ('تلاش ناموفق' if fa else 'Failed/locked attempts',current['totals']['failure']+current['totals']['locked']),
        ('نرخ موفقیت' if fa else 'Success rate',str(current['success_rate'])+'%'),
        ('تغییر نسبت به بازه قبل' if fa else 'Change vs previous period',f"{result['failed_delta']:+d}"),
        ('تلاش ناموفق بازه قبل' if fa else 'Previous period failures',previous['totals']['failure']+previous['totals']['locked']),
    ]
