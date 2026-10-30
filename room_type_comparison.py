"""Authorized, indicative room-type period comparisons."""
from datetime import date, timedelta
from room_type_analytics import room_type_performance

def compare_room_types(conn, *, branch_id, start, end, user_id, role):
    begin, finish = date.fromisoformat(start), date.fromisoformat(end)
    days = (finish-begin).days
    if not 1 <= days <= 183:
        raise ValueError('Comparison period must be 1–183 days')
    prior = (begin-timedelta(days=days)).isoformat()
    options = dict(branch_id=branch_id,user_id=user_id,role=role)
    current = {r['kind']:r for r in room_type_performance(conn,start=start,end=end,**options)}
    previous = {r['kind']:r for r in room_type_performance(conn,start=prior,end=start,**options)}
    def difference(a,b):
        return round(a-b,2) if a is not None and b is not None else None
    result=[]
    for kind in sorted(set(current)|set(previous)):
        a=current.get(kind,{}); b=previous.get(kind,{})
        result.append(dict(kind=kind,
            occupancy_now=a.get('occupancy_percent'),occupancy_delta_pp=difference(a.get('occupancy_percent'),b.get('occupancy_percent')),
            adr_now=a.get('estimated_adr'),adr_delta=difference(a.get('estimated_adr'),b.get('estimated_adr')),
            revpar_now=a.get('estimated_revpar'),revpar_delta=difference(a.get('estimated_revpar'),b.get('estimated_revpar')),
            missing_quotes=a.get('missing_quotes',0)+b.get('missing_quotes',0)))
    return {'previous_start':prior,'previous_end':start,'rows':result}
