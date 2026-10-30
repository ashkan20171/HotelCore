import unittest
from translation_audit import untranslated, translation_coverage
from localization import translate

class TranslationAuditTests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(untranslated(['رزرو جدید', 'ناشناخته']), ['ناشناخته'])
    def test_unique(self):
        self.assertEqual(translation_coverage(['رزرو جدید', 'رزرو جدید', 'ناشناخته']), (1,2))
    def test_empty(self):
        self.assertEqual(translation_coverage([]), (0,0))
    def test_booking_error_translation(self):
        self.assertEqual(translate('نام مهمان الزامی است.', 'en'), 'Guest name is required.')
    def test_farsi_unchanged(self):
        self.assertEqual(translate('نام مهمان الزامی است.', 'fa'), 'نام مهمان الزامی است.')

if __name__ == '__main__': unittest.main()
