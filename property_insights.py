"""Pure presentation helpers for branch-authorized executive scorecards."""
import math

METRICS=('occupancy_percent','estimated_adr','estimated_revpar','estimated_value')

def filtered_rankings(rows, *, search='', metric='occupancy_percent', descending=True, only_alerts=False):
    if metric not in METRICS:
        raise ValueError('Unsupported KPI')
    query=search.strip().casefold()
    selected=[r for r in rows if (not query or query in str(r['branch_name']).casefold())
              and (not only_alerts or bool(r.get('alerts')))]
    def key(row):
        v=row.get(metric)
        if v is None or not isinstance(v,(int,float)) or not math.isfinite(v):
            return (1,0,str(row['branch_name']).casefold())
        return (0,-v if descending else v,str(row['branch_name']).casefold())
    return sorted(selected,key=key)

def chart_bars(rows, *, metric='occupancy_percent'):
    if metric not in METRICS: raise ValueError('Unsupported KPI')
    valid=[r[metric] for r in rows if isinstance(r.get(metric),(int,float)) and math.isfinite(r[metric]) and r[metric]>=0]
    maximum=max(valid,default=0)
    return [{'branch_name':r['branch_name'], 'value':r.get(metric),
             'percent':round(100*r[metric]/maximum) if maximum and isinstance(r.get(metric),(int,float)) and math.isfinite(r[metric]) and r[metric]>=0 else 0}
            for r in rows]
