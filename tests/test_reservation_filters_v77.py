import unittest
from reservation_filters import normalize_query, matches_reservation, status_options, status_color

class ReservationFiltersTests(unittest.TestCase):
    def setUp(self):
        self.row=['۱۲','۱۰۱','علي كريمي','۱۴۰۵/۰۸/۰۱','۱۴۰۵/۰۸/۰۳','رزرو شده']
    def test_persian_arabic_letters(self):
        self.assertTrue(matches_reservation(self.row,'علی کریمی'))
    def test_digits(self):
        self.assertTrue(matches_reservation(self.row,'101'))
    def test_status_match(self):
        self.assertTrue(matches_reservation(self.row,'','رزرو شده'))
    def test_status_mismatch(self):
        self.assertFalse(matches_reservation(self.row,'','لغو شده'))
    def test_search_mismatch(self):
        self.assertFalse(matches_reservation(self.row,'missing'))
    def test_all_status(self):
        self.assertTrue(matches_reservation(self.row,'',None))
    def test_english_labels(self):
        self.assertEqual(status_options('en')[0][0],'All statuses')
    def test_palette(self):
        self.assertTrue(status_color('لغو شده')[0].startswith('#'))
    def test_normalize(self):
        self.assertEqual(normalize_query('  كيان  '),'کیان')

if __name__=='__main__': unittest.main()
