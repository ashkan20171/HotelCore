"""Authorized multi-property comparison against an equal-length preceding period."""
from datetime import date, timedelta
from multi_property_dashboard import branch_scorecard

FIELDS=('occupancy_percent','estimated_adr','estimated_revpar','estimated_value')

def compare_property_periods(conn, *, user_id, role, start, end, branch_ids=None, low_occupancy=40):
    first,last=date.fromisoformat(start),date.fromisoformat(end)
    days=(last-first).days
    if not 1<=days<=90:
        raise ValueError('Period must be 1–90 days')
    old_start=(first-timedelta(days=days)).isoformat()
    kw=dict(user_id=user_id,role=role,branch_ids=branch_ids,low_occupancy=low_occupancy)
    current=branch_scorecard(conn,start=start,end=end,**kw)
    previous=branch_scorecard(conn,start=old_start,end=start,**kw)
    previous_by_id={r['branch_id']:r for r in previous}
    def change(a,b):
        return round(a-b,2) if a is not None and b is not None else None
    rows=[]
    for row in current:
        before=previous_by_id.get(row['branch_id'],{})
        rows.append({**row,'previous':before,'changes':{f:change(row.get(f),before.get(f)) for f in FIELDS}})
    return {'start':start,'end':end,'previous_start':old_start,'previous_end':start,'rows':rows}
