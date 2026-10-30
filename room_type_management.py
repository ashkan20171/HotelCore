"""Indicative room-type ranking, alert thresholds and portable CSV exports."""
import csv
import math

METRICS = ('estimated_revpar', 'estimated_adr', 'occupancy_percent', 'estimated_value')

def ranked_room_types(rows, metric='estimated_revpar'):
    if metric not in METRICS:
        raise ValueError('Unsupported ranking metric')
    def score(row):
        value=row.get(metric)
        if value is None: return float('-inf')
        value=float(value)
        return value if math.isfinite(value) else float('-inf')
    return sorted(rows, key=lambda row: (-score(row), str(row.get('kind',''))))

def room_type_risks(rows, *, low_occupancy=40.0, high_missing_quotes=0):
    if not 0 <= low_occupancy <= 100 or high_missing_quotes < 0:
        raise ValueError('Invalid warning threshold')
    warnings=[]
    for row in rows:
        kind=str(row.get('kind',''))
        occupancy=row.get('occupancy_percent')
        if occupancy is not None and float(occupancy) < low_occupancy:
            warnings.append((kind,'low_occupancy',round(float(occupancy),2)))
        if int(row.get('missing_quotes') or 0) > high_missing_quotes:
            warnings.append((kind,'missing_quotes',int(row['missing_quotes'])))
    return warnings

def export_room_type_ranking_csv(path, rows, *, metric='estimated_revpar'):
    ranked=ranked_room_types(rows,metric)
    fields=('kind','occupancy_percent','occupied_nights','estimated_value',
            'estimated_adr','estimated_revpar','missing_quotes')
    with open(path,'w',encoding='utf-8-sig',newline='') as handle:
        writer=csv.writer(handle)
        writer.writerow(fields)
        for row in ranked:
            writer.writerow([row.get(key,'') if row.get(key) is not None else '' for key in fields])
    return len(ranked)
