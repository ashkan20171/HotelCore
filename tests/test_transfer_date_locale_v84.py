import unittest
from transfer_date_locale import normalize_report_date, report_date

class TestLocalizedTransferDates(unittest.TestCase):
    def test_gregorian(self):
        self.assertEqual(normalize_report_date('2026-10-22','en'),'2026-10-22')
    def test_jalali_digits(self):
        try: import jdatetime
        except ImportError: self.skipTest('jdatetime unavailable')
        self.assertEqual(normalize_report_date('۱۴۰۵/۰۷/۳۰','fa'),'2026-10-22')
        self.assertEqual(report_date('2026-10-22','fa'),'1405-07-30')
    def test_invalid(self):
        with self.assertRaises(ValueError): normalize_report_date('2026-13-22','en')
        with self.assertRaises(ValueError): normalize_report_date('bad','fa')
