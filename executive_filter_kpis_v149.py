"""Deterministic, display-only KPIs for a filtered authorized daily snapshot."""
from executive_financial_filters_v148 import filter_daily_series

def filtered_kpis(series, **options):
    selected=filter_daily_series(series,**options)
    income=sum(row['income'] for row in selected)
    expenses=sum(row['expenses'] for row in selected)
    return {'days':len(selected),'total_days':len(series),'income':income,
            'expenses':expenses,'difference':income-expenses}

def yoy_chart_values(yoy):
    """Normalize three YoY metrics for rendering; preserve negative net amounts."""
    metrics=yoy.get('metrics',{})
    values=[]
    for key in ('income','expenses','difference'):
        metric=metrics.get(key)
        if not isinstance(metric,dict):continue
        current=metric.get('current');previous=metric.get('previous')
        if type(current) not in (int,float) or type(previous) not in (int,float):
            raise ValueError('Invalid YoY amount')
        values.append({'key':key,'current':current,'previous':previous})
    return values
