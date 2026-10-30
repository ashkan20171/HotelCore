"""Pure occupancy calculations; reservation intervals are [checkin, checkout)."""
from datetime import date, timedelta

ACTIVE_STATUSES = frozenset({'رزرو شده', 'پذیرش شده'})

def build_grid(rooms, reservations, start, days=14):
    if not 1 <= days <= 90:
        raise ValueError('days must be between 1 and 90')
    if isinstance(start, str):
        start = date.fromisoformat(start)
    dates = [start + timedelta(days=i) for i in range(days)]
    grid = {room_id: ['آزاد'] * days for room_id, _ in rooms}
    for room_id, checkin, checkout, status in reservations:
        if room_id not in grid or status not in ACTIVE_STATUSES:
            continue
        begin, end = date.fromisoformat(checkin), date.fromisoformat(checkout)
        if end <= begin:
            continue
        for i, day in enumerate(dates):
            if begin <= day < end:
                grid[room_id][i] = 'پذیرش شده' if status == 'پذیرش شده' else ('رزرو شده' if grid[room_id][i] == 'آزاد' else grid[room_id][i])
    return dates, grid

def occupancy_summary(grid, days):
    rooms = len(grid)
    occupied = sum(cell != 'آزاد' for cells in grid.values() for cell in cells)
    capacity = rooms * days
    return {'occupied_room_nights': occupied, 'available_room_nights': capacity - occupied,
            'occupancy_percent': round(100 * occupied / capacity, 1) if capacity else 0.0}
