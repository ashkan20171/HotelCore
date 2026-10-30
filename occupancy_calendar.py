"""Presentation helpers for the branch-scoped occupancy calendar."""

COLORS = {'آزاد':'#0f766e','رزرو شده':'#b45309','پذیرش شده':'#9f1239'}
ENGLISH = {'آزاد':'Available','رزرو شده':'Reserved','پذیرش شده':'Checked in'}

def cell_color(status):
    return COLORS.get(status, '#64748b')

def cell_description(status, language='fa'):
    return ENGLISH.get(status,status) if language == 'en' else status

def is_bookable(status):
    return status == 'آزاد'


def matching_bookings(bookings, room_id, day):
    """Find bookings occupying a room on a day; checkout is exclusive."""
    return [booking for booking in bookings
            if int(booking[0]) == int(room_id) and booking[1] <= day < booking[2]
            and booking[3] not in ('لغو شده', 'cancelled', 'canceled')]
