"""Indicative accommodation KPIs by current room type, scoped to authorized branch.

Not recognized revenue: quotes are spread across nights; room transfers and historical
inventory changes cannot be reconstructed from the current room table.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from branch_access import require_branch
from stay_performance import allocated_quote


def room_type_performance(conn, *, branch_id, start, end, user_id, role):
    require_branch(conn, user_id, role, branch_id)
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if last <= first or (last-first).days > 366:
        raise ValueError('Reporting window must be 1–366 days')
    inventory = conn.execute("SELECT COALESCE(NULLIF(TRIM(kind),''),'Unknown'), COUNT(*) FROM rooms WHERE branch_id=? AND status='فعال' GROUP BY COALESCE(NULLIF(TRIM(kind),''),'Unknown')", (branch_id,)).fetchall()
    data = defaultdict(lambda: {'rooms':0, 'occupied_nights':0, 'estimated_value':Decimal(0), 'missing_quotes':0})
    for kind, count in inventory:
        data[kind]['rooms'] = count
    rows = conn.execute('''SELECT COALESCE(NULLIF(TRIM(m.kind),''),'Unknown'),r.checkin,r.checkout,b.accommodation_total
        FROM reservations r JOIN rooms m ON m.id=r.room_id AND m.branch_id=r.branch_id
        LEFT JOIN booking_rates b ON b.reservation_id=r.id
        WHERE r.branch_id=? AND r.status<>'لغو شده' AND r.checkin<? AND r.checkout>?''', (branch_id,end,start)).fetchall()
    for kind, checkin, checkout, amount in rows:
        nights = max(0, (min(date.fromisoformat(checkout),last)-max(date.fromisoformat(checkin),first)).days)
        if not nights:
            continue
        item=data[kind]
        item['occupied_nights'] += nights
        if amount is None:
            item['missing_quotes'] += 1
        else:
            portion, _ = allocated_quote(amount,checkin,checkout,start,end)
            item['estimated_value'] += portion
    output=[]
    for kind, item in sorted(data.items()):
        capacity=item['rooms']*(last-first).days
        occupied=item['occupied_nights']
        incomplete=bool(item['missing_quotes'])
        value=item['estimated_value']
        def ratio(denominator):
            return float((value/denominator).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) if denominator and not incomplete else None
        output.append({'kind':kind, 'rooms':item['rooms'], 'capacity_nights':capacity,
            'occupied_nights':occupied, 'occupancy_percent':round(100*occupied/capacity,1) if capacity else None,
            'estimated_value':int(value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
            'estimated_adr':ratio(occupied), 'estimated_revpar':ratio(capacity),
            'missing_quotes':item['missing_quotes'], 'overcapacity':occupied>capacity})
    return output


def room_type_alerts(rows, language='fa'):
    if language not in ('fa','en'):
        raise ValueError('Unsupported language')
    fa=language=='fa'; messages=[]
    for row in rows:
        kind=row['kind']
        if row['overcapacity']:
            messages.append((f'{kind}: اشغال بیشتر از ظرفیت فعلی است.' if fa else f'{kind}: occupied nights exceed current capacity.'))
        if row['missing_quotes']:
            messages.append((f'{kind}: {row["missing_quotes"]} رزرو بدون نرخ دارد.' if fa else f'{kind}: {row["missing_quotes"]} reservations lack quotes.'))
        if row['occupancy_percent'] is not None and row['occupancy_percent'] < 35:
            messages.append((f'{kind}: نرخ اشغال کمتر از ۳۵٪ است.' if fa else f'{kind}: occupancy is below 35%.'))
    return messages
