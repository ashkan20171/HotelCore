"""Presentation-only KPI formatting and side-by-side ADR/RevPAR comparison."""
from math import isfinite

def kpi_display(totals, language='fa'):
    if language not in ('fa','en'): raise ValueError('Unsupported language')
    fa=language=='fa'
    occupancy=totals.get('occupancy_percent')
    return [
        ('شعب فعال' if fa else 'Properties', str(totals.get('branches',0))),
        ('اتاق فعال' if fa else 'Active rooms', str(totals.get('rooms',0))),
        ('نرخ اشغال' if fa else 'Occupancy', '—' if occupancy is None else f'{occupancy:.1f}%'),
        ('ADR تخمینی' if fa else 'Indicative ADR', _money(totals.get('estimated_adr'))),
        ('RevPAR تخمینی' if fa else 'Indicative RevPAR', _money(totals.get('estimated_revpar'))),
        ('رزرو بدون نرخ' if fa else 'Missing quotes', str(totals.get('missing_quotes',0))),
    ]

def _money(value):
    return '—' if value is None else f'{value:,.2f}'

def comparative_bars(rows, metric, limit=10):
    if metric not in ('estimated_adr','estimated_revpar'):raise ValueError('Unsupported comparison metric')
    if not 1<=limit<=100:raise ValueError('Invalid limit')
    valid=[]
    for row in rows:
        value=row.get(metric)
        if value is None:continue
        value=float(value)
        if isfinite(value) and value>=0:
            valid.append({'branch_name':str(row.get('branch_name','')),'value':value})
    valid.sort(key=lambda r:(-r['value'],r['branch_name']))
    valid=valid[:limit]
    top=max((r['value'] for r in valid),default=0)
    for row in valid:row['percent']=round(100*row['value']/top) if top else 0
    return valid
