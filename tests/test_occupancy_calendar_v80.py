import unittest
from occupancy_calendar import matching_bookings

class CalendarDetailsTests(unittest.TestCase):
    def test_checkout_exclusive(self):
        bookings=[(1,'2026-10-20','2026-10-23','رزرو شده')]
        self.assertEqual(len(matching_bookings(bookings,1,'2026-10-22')),1)
        self.assertEqual(matching_bookings(bookings,1,'2026-10-23'),[])
    def test_room_isolation(self):
        self.assertEqual(matching_bookings([(2,'2026-10-20','2026-10-23','رزرو شده')],1,'2026-10-21'),[])
    def test_cancelled_excluded(self):
        self.assertEqual(matching_bookings([(1,'2026-10-20','2026-10-23','لغو شده')],1,'2026-10-21'),[])
