import unittest
from table_filters import normalize, row_matches

class TableFilterTests(unittest.TestCase):
    def test_empty_query(self): self.assertTrue(row_matches(['اتاق ۱۰۱'],'  '))
    def test_persian_arabic_forms(self): self.assertTrue(row_matches(['علی کاظمی'],'علي كاظمي'))
    def test_digits(self): self.assertTrue(row_matches(['رزرو ۱۲۳'],'123'))
    def test_multi_terms(self): self.assertTrue(row_matches(['اتاق 101','مهمان رضایی'],'رضایی ۱۰۱'))
    def test_no_match(self): self.assertFalse(row_matches(['رزرو شده'],'لغو'))
    def test_case(self): self.assertTrue(row_matches(['VIP Guest'],'vip'))
    def test_normalize_none(self): self.assertEqual(normalize(None),'')
