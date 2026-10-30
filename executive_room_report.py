"""Authorized branch comparisons and safe CSV exports of indicative room-type KPIs."""
import csv
import math
from branch_access import allowed_branches, require_branch
from room_type_analytics import room_type_performance

def validate_thresholds(low_occupancy, missing_quotes):
    if isinstance(low_occupancy,bool) or not isinstance(low_occupancy,(int,float)) or not math.isfinite(low_occupancy) or not 0<=low_occupancy<=100:
        raise ValueError("Occupancy threshold must be 0..100")
    if isinstance(missing_quotes,bool) or not isinstance(missing_quotes,int) or not 0<=missing_quotes<=10000:
        raise ValueError("Missing quote threshold must be 0..10000")
    return int(low_occupancy),missing_quotes

def branch_room_type_comparison(conn, *, branch_ids, start, end, user_id, role):
    """Compare only explicitly selected and authorized branches; no guest details."""
    if not branch_ids or len(branch_ids)>100 or len(set(branch_ids))!=len(branch_ids):
        raise ValueError("Select 1–100 distinct branches")
    names=dict(allowed_branches(conn,user_id,role))
    results=[]
    for branch_id in branch_ids:
        require_branch(conn,user_id,role,branch_id)
        for item in room_type_performance(conn,branch_id=branch_id,start=start,end=end,user_id=user_id,role=role):
            results.append({'branch_id':branch_id,'branch_name':names[branch_id],**item})
    return results

def _safe_cell(value):
    if value is None:return ''
    text=str(value)
    if text.lstrip().startswith(('=','+','-','@','\\t','\\r','\\n')):
        return "'"+text
    return text

def export_branch_comparison_csv(path,rows):
    fields=('branch_id','branch_name','kind','rooms','capacity_nights','occupied_nights',
            'occupancy_percent','estimated_value','estimated_adr','estimated_revpar','missing_quotes','overcapacity')
    with open(path,'w',encoding='utf-8-sig',newline='') as output:
        writer=csv.writer(output)
        writer.writerow(fields)
        for item in rows:writer.writerow([_safe_cell(item.get(key)) for key in fields])
    return len(rows)
