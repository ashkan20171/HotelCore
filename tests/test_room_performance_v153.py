import unittest
from room_performance_v153 import performance_rows,performance_summary

ROWS=[{'type':'Suite','rooms':2,'available_days':2,'booked_nights':2,'booked_value':400,'estimated_adr':200,'estimated_revpar':100,'occupancy_pct':50},
      {'type':'Standard','rooms':1,'available_days':2,'booked_nights':1,'booked_value':80,'estimated_adr':80,'estimated_revpar':40,'occupancy_pct':50}]
class RoomPerformanceTests(unittest.TestCase):
    def test_rank(self):self.assertEqual(performance_rows(ROWS)[0]['type'],'Suite')
    def test_other_metric(self):self.assertEqual(performance_rows(ROWS,'booked_value')[0]['type'],'Suite')
    def test_weighted(self):
        s=performance_summary(ROWS)
        self.assertEqual(s['total_booked_value'],480)
        self.assertEqual(s['weighted_adr'],160)
        self.assertEqual(s['weighted_revpar'],80)
        self.assertEqual(s['occupancy_pct'],50)
    def test_empty(self):self.assertEqual(performance_summary([])['types'],0)
    def test_invalid_metric(self):
        with self.assertRaises(ValueError):performance_rows(ROWS,'profit')
    def test_nan(self):
        with self.assertRaises(ValueError):performance_rows([{**ROWS[0],'estimated_adr':float('nan')}])
