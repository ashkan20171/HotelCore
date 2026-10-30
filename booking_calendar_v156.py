"""Calendar-ready booking coverage and actionable risk summaries. No demand prediction."""
from datetime import date
from collections import Counter


def calendar_weeks(rows, *, week_start=5):
    """Saturday-first (5) or Monday-first (0) calendar with None padding."""
    if type(week_start) is not int or not 0 <= week_start <= 6:
        raise ValueError('Invalid first weekday')
    days = []
    previous = None
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid booking row')
        day = date.fromisoformat(row['date'])
        if previous is not None and (day - previous).days != 1:
            raise ValueError('Booking rows must be consecutive')
        previous = day
        days.append(dict(row))
    if not days:
        return []
    offset = (date.fromisoformat(days[0]['date']).weekday() - week_start) % 7
    padded = [None] * offset + days
    padded += [None] * ((-len(padded)) % 7)
    return [padded[i:i+7] for i in range(0, len(padded), 7)]


def coverage_band(row, *, high_threshold=80):
    """Return low, medium, high or unavailable for recorded booking coverage."""
    if type(high_threshold) not in (int, float) or not 0 <= high_threshold <= 100:
        raise ValueError('Invalid high threshold')
    if type(row.get('total_rooms')) is not int or row['total_rooms'] < 0:
        raise ValueError('Invalid room count')
    pct = row.get('booked_pct')
    if type(pct) not in (int, float) or not 0 <= pct <= 100:
        raise ValueError('Invalid coverage')
    if row['total_rooms'] == 0:
        return 'unavailable'
    if bool(row.get('low_demand')):
        return 'low'
    return 'high' if pct >= high_threshold else 'medium'


def coverage_insights(rows, *, high_threshold=80):
    """Aggregate unique day counts and consecutive low-coverage streaks."""
    weeks = calendar_weeks(rows)
    days = [day for week in weeks for day in week if day is not None]
    counts = Counter(coverage_band(day, high_threshold=high_threshold) for day in days)
    longest = current = 0
    longest_start = current_start = None
    for day in days:
        if coverage_band(day, high_threshold=high_threshold) == 'low':
            if current == 0:
                current_start = day['date']
            current += 1
            if current > longest:
                longest, longest_start = current, current_start
        else:
            current = 0
    return {'days': len(days), 'low': counts['low'], 'medium': counts['medium'],
            'high': counts['high'], 'unavailable': counts['unavailable'],
            'longest_low_streak': longest, 'longest_low_start': longest_start}
