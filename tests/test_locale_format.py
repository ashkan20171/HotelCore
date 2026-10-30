import unittest
from locale_format import display_date, display_money, jdatetime

class LocaleFormattingTests(unittest.TestCase):
    def test_gregorian_english(self):
        self.assertEqual(display_date('2026-10-20','en'),'2026-10-20')
    @unittest.skipIf(jdatetime is None, "jdatetime dependency unavailable in test environment")
    def test_jalali_persian(self):
        self.assertEqual(display_date('2026-03-21','fa'),'1405/01/01')
    def test_invalid_date_preserved(self):
        self.assertEqual(display_date('unknown','en'),'unknown')
    def test_none(self):
        self.assertEqual(display_date(None,'fa'),'')
    def test_money_persian(self):
        self.assertEqual(display_money(1250000,'fa'),'1,250,000 تومان')
    def test_money_english_no_fx(self):
        self.assertEqual(display_money(1250000,'en'),'1,250,000 toman')
    def test_negative_money(self):
        self.assertEqual(display_money(-500,'en'),'-500 toman')
