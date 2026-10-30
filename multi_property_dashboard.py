"""Authorized multi-property executive overview of indicative room performance."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from branch_access import allowed_branches, require_branch
from room_type_analytics import room_type_performance

def branch_scorecard(conn, *, user_id, role, start, end, branch_ids=None, low_occupancy=40):
    first,last=date.fromisoformat(start),date.fromisoformat(end)
    if not 1 <= (last-first).days <= 90: raise ValueError('Reporting window must be 1–90 days')
    if not 0 <= low_occupancy <= 100: raise ValueError('Invalid occupancy threshold')
    permitted=dict(allowed_branches(conn,user_id,role))
    ids=list(permitted) if branch_ids is None else list(branch_ids)
    if len(ids)>100 or len(set(ids))!=len(ids): raise ValueError('Too many or duplicate branches')
    results=[]
    for branch_id in ids:
        require_branch(conn,user_id,role,branch_id)
        types=room_type_performance(conn,branch_id=branch_id,start=start,end=end,user_id=user_id,role=role)
        capacity=sum(r['capacity_nights'] for r in types)
        occupied=sum(r['occupied_nights'] for r in types)
        estimated=sum(r['estimated_value'] for r in types)
        missing=sum(r['missing_quotes'] for r in types)
        overcapacity=any(r['overcapacity'] for r in types) or occupied>capacity
        occupancy=round(100*occupied/capacity,1) if capacity else None
        adr=round(estimated/occupied,2) if occupied and not missing else None
        revpar=round(estimated/capacity,2) if capacity and not missing else None
        alerts=[]
        if missing:alerts.append('missing_quotes')
        if overcapacity:alerts.append('overcapacity')
        if occupancy is None:alerts.append('no_active_rooms')
        elif occupancy<low_occupancy:alerts.append('low_occupancy')
        results.append(dict(branch_id=branch_id,branch_name=permitted[branch_id],
          rooms=sum(r['rooms'] for r in types),capacity_nights=capacity,occupied_nights=occupied,
          occupancy_percent=occupancy,estimated_value=estimated,estimated_adr=adr,
          estimated_revpar=revpar,missing_quotes=missing,alerts=alerts))
    return results

def overview_totals(rows):
    capacity=sum(r['capacity_nights'] for r in rows)
    occupied=sum(r['occupied_nights'] for r in rows)
    value=sum(r['estimated_value'] for r in rows)
    missing=sum(r['missing_quotes'] for r in rows)
    return {'branches':len(rows),'rooms':sum(r['rooms'] for r in rows),
      'occupancy_percent':round(100*occupied/capacity,1) if capacity else None,
      'estimated_value':value,'estimated_adr':round(value/occupied,2) if occupied and not missing else None,
      'estimated_revpar':round(value/capacity,2) if capacity and not missing else None,
      'missing_quotes':missing}
