import unittest
from datetime import date,timedelta
from booking_calendar_v156 import calendar_weeks,coverage_band,coverage_insights

class CalendarTests(unittest.TestCase):
    def make(self,start,count,low=(0,1,2)):
        return [{'date':(start+timedelta(days=i)).isoformat(),'total_rooms':10,
                 'booked_rooms':2 if i in low else 9,'booked_pct':20 if i in low else 90,
                 'low_demand':i in low} for i in range(count)]
    def test_saturday_first(self):
        weeks=calendar_weeks(self.make(date(2026,11,1),7))
        self.assertEqual(len(weeks),2)
        self.assertIsNone(weeks[0][0]);self.assertEqual(weeks[0][1]['date'],'2026-11-01')
    def test_monday_first(self):
        weeks=calendar_weeks(self.make(date(2026,11,2),7),week_start=0)
        self.assertEqual(len(weeks),1)
    def test_streak(self):
        info=coverage_insights(self.make(date(2026,11,1),6))
        self.assertEqual((info['low'],info['high'],info['longest_low_streak']),(3,3,3))
        self.assertEqual(info['longest_low_start'],'2026-11-01')
    def test_zero_rooms(self):
        self.assertEqual(coverage_band({'total_rooms':0,'booked_pct':0,'low_demand':False}),'unavailable')
    def test_nonconsecutive(self):
        rows=self.make(date(2026,11,1),3);rows[1]['date']='2026-11-08'
        with self.assertRaises(ValueError):calendar_weeks(rows)
    def test_bad_threshold(self):
        with self.assertRaises(ValueError):coverage_band({'total_rooms':2,'booked_pct':50},high_threshold=110)
    def test_empty(self):
        self.assertEqual(calendar_weeks([]),[])
        self.assertEqual(coverage_insights([])['days'],0)
