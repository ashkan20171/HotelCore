"""Pure-Python security trend chart presentation and bounded KPI calculations."""
from security_report_v110 import daily_login_trends


def chart_data(conn, actor_id, *, days=7, username=None, now=None):
    rows = daily_login_trends(conn, actor_id, days=days, username=username, now=now)
    series = [{'date': day, 'success': ok, 'failure': fail, 'locked': locked}
              for day, ok, fail, locked in rows]
    totals = {key: sum(row[key] for row in series) for key in ('success', 'failure', 'locked')}
    attempts = sum(totals.values())
    return {'series': series, 'totals': totals,
            'success_rate': round(totals['success'] * 100 / attempts, 1) if attempts else 0.0,
            'peak_failures': max((row['failure'] + row['locked'] for row in series), default=0)}
