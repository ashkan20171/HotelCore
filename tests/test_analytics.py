import unittest
from datetime import date
from analytics import occupancy_rate, overlap, average_daily_rate

class AnalyticsTests(unittest.TestCase):
    def test_occupancy(self):
        self.assertEqual(occupancy_rate(7, 10), 70.0)
        self.assertEqual(occupancy_rate(0, 0), 0.0)
    def test_no_double_booking_for_adjacent_stays(self):
        self.assertFalse(overlap(date(2026,1,1),date(2026,1,3),date(2026,1,3),date(2026,1,5)))
    def test_overlap(self):
        self.assertTrue(overlap(date(2026,1,1),date(2026,1,4),date(2026,1,3),date(2026,1,5)))
    def test_adr(self):
        self.assertEqual(average_daily_rate(6000000,3),2000000)
        self.assertEqual(average_daily_rate(0,0),0)
if __name__=='__main__': unittest.main()
