import unittest
try:
 from occupancy_trend_chart import normalized_occupancy
except ImportError:
 normalized_occupancy=None

@unittest.skipIf(normalized_occupancy is None,'PySide6 unavailable')
class TrendTests(unittest.TestCase):
 def test_empty(self): self.assertEqual(normalized_occupancy([]),[])
 def test_missing(self): self.assertEqual(normalized_occupancy([{'date':'2026-01-01','occupancy_percent':None}]),[])
 def test_bounds(self):
  self.assertEqual(normalized_occupancy([{'date':'2026-01-01','occupancy_percent':-5},{'date':'2026-01-02','occupancy_percent':120}]),[('2026-01-01',0.0),('2026-01-02',100.0)])
