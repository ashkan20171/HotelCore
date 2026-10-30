import unittest
from datetime import date
from executive_jalali_v143 import jalali_label,parse_jalali
try:
    import jdatetime
except ImportError:
    jdatetime=None

@unittest.skipIf(jdatetime is None, "jdatetime is not installed in test environment")
class JalaliTests(unittest.TestCase):
    def test_nowruz(self):self.assertEqual(parse_jalali('1405/01/01'),date(2026,3,21))
    def test_roundtrip(self):
        for d in (date(2026,10,23),date(2024,2,29),date(2025,12,31)):
            self.assertEqual(parse_jalali(jalali_label(d)),d)
    def test_reject_bad(self):
        for value in ('1405/13/01','1405/02/32','1405-01-01','1405/1/01','abc','9999/01/01'):
            with self.subTest(value=value),self.assertRaises(ValueError):parse_jalali(value)
