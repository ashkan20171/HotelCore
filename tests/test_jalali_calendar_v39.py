import unittest
try:
 from jalali_calendar import jalali_from_iso, iso_from_jalali, jalali_month_days
except ImportError:
 jalali_from_iso = None

@unittest.skipIf(jalali_from_iso is None, 'jdatetime is not installed')
class JalaliCalendarTests(unittest.TestCase):
 def test_nowruz_1403(self):
  self.assertEqual(iso_from_jalali(1403,1,1),'2024-03-20')
 def test_roundtrip(self):
  for value in ('2024-03-20','2025-01-01','2026-10-20'):
   j=jalali_from_iso(value)
   self.assertEqual(iso_from_jalali(j.year,j.month,j.day),value)
 def test_first_six_months(self):
  self.assertEqual(jalali_month_days(1403,6),31)
 def test_seventh_month(self):
  self.assertEqual(jalali_month_days(1403,7),30)
 def test_leap_esfand(self):
  self.assertEqual(jalali_month_days(1399,12),30)
 def test_regular_esfand(self):
  self.assertEqual(jalali_month_days(1400,12),29)
 def test_invalid_day(self):
  with self.assertRaises(ValueError):iso_from_jalali(1400,12,30)
 def test_invalid_month(self):
  with self.assertRaises(ValueError):iso_from_jalali(1403,13,1)
