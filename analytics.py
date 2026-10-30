"""Pure analytical helpers for the hotel dashboard."""
from datetime import date, timedelta

def occupancy_rate(occupied: int, capacity: int) -> float:
    if capacity <= 0:
        return 0.0
    return round(max(0, min(occupied, capacity)) * 100 / capacity, 1)

def overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    """Hotel checkout dates are exclusive."""
    if end_a <= start_a or end_b <= start_b:
        raise ValueError("Checkout must be later than check-in")
    return start_a < end_b and start_b < end_a

def average_daily_rate(room_revenue: int, sold_room_nights: int) -> float:
    return round(room_revenue / sold_room_nights, 2) if sold_room_nights > 0 else 0.0
