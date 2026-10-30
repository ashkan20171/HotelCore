"""Compare authorized branch cash movement with an equal-length previous period."""
from datetime import date, timedelta


def previous_interval(start, end):
    """ISO half-open periods: [start, end) and preceding equal-length period."""
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if a >= b:
        raise ValueError('End must follow start')
    return (a - (b - a)).isoformat(), a.isoformat()


def branch_period_insights(current, previous):
    """Both mappings must contain only already-authorized branch IDs."""
    if set(current) != set(previous):
        raise ValueError('Periods must cover identical authorized branches')
    results = []
    for branch_id, now in current.items():
        before = previous[branch_id]
        net = int(now['net_cash_movement'])
        old = int(before['net_cash_movement'])
        delta = net - old
        results.append({'branch_id': branch_id, 'net': net, 'previous_net': old,
                        'change': delta, 'direction': 'up' if delta > 0 else 'down' if delta < 0 else 'flat',
                        'change_percent': None if old == 0 else (delta / abs(old)) * 100})
    return results


def insight_caption(insights, language='fa'):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    rising = sum(x['direction'] == 'up' for x in insights)
    falling = sum(x['direction'] == 'down' for x in insights)
    negative = sum(x['net'] < 0 for x in insights)
    if language == 'fa':
        return f'بهبود خالص نسبت به دوره قبل: {rising} شعبه  |  کاهش خالص: {falling} شعبه  |  خالص منفی در دوره جاری: {negative} شعبه'
    return f'Net improved: {rising} branches  |  Net declined: {falling} branches  |  Current negative net: {negative} branches'
