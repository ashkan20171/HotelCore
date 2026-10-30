"""Room-type booking performance indicators, not recognized profit or revenue."""
from math import isfinite

def performance_rows(rows,metric='estimated_revpar'):
    allowed=('estimated_adr','estimated_revpar','occupancy_pct','booked_value')
    if metric not in allowed:raise ValueError('Unsupported performance metric')
    result=[]
    for row in rows:
        if not isinstance(row,dict):raise ValueError('Invalid room row')
        values={}
        for key in allowed:
            number=row.get(key)
            if type(number) not in (int,float) or not isfinite(number) or number<0:
                raise ValueError('Invalid room performance value')
            values[key]=float(number)
        name=str(row.get('type','')).strip()
        if not name:raise ValueError('Room type is required')
        result.append({'type':name,**values})
    return sorted(result,key=lambda row:(-row[metric],row['type'].casefold()))

def performance_summary(rows):
    ranked=performance_rows(rows)
    if not ranked:return {'types':0,'leader':None,'total_booked_value':0,'weighted_adr':0,'weighted_revpar':0,'occupancy_pct':0}
    total_value=sum(float(r['booked_value']) for r in rows)
    nights=sum(float(r['booked_nights']) for r in rows)
    available=sum(float(r['rooms'])*float(r['available_days']) for r in rows)
    if any(float(r['booked_nights'])<0 or float(r['rooms'])<0 or float(r['available_days'])<0 for r in rows):
        raise ValueError('Negative capacity')
    return {'types':len(ranked),'leader':ranked[0]['type'],'total_booked_value':round(total_value,2),
            'weighted_adr':round(total_value/nights,2) if nights else 0,
            'weighted_revpar':round(total_value/available,2) if available else 0,
            'occupancy_pct':round(100*nights/available,1) if available else 0}
