import unittest
from localization import translate, localize_errors

class LocaleWorkflowTests(unittest.TestCase):
    def test_persian_default(self):
        self.assertEqual(translate('اتاق جدید'), 'اتاق جدید')
    def test_room_title(self):
        self.assertEqual(translate('اتاق جدید', 'en'), 'New room')
    def test_room_number(self):
        self.assertEqual(translate('شماره اتاق:', 'en'), 'Room number:')
    def test_room_type(self):
        self.assertEqual(translate('دلوکس', 'en'), 'Deluxe')
    def test_payment_validation(self):
        self.assertEqual(translate('اعتبارسنجی پرداخت', 'en'), 'Payment validation')
    def test_error_dict_preserves_keys(self):
        self.assertEqual(localize_errors({'room':'اتاق جدید'}, 'en'), {'room':'New room'})
    def test_error_list(self):
        self.assertEqual(localize_errors(['خطا'], 'en'), ['Error'])
    def test_unknown_unchanged(self):
        self.assertEqual(translate('A guest name', 'en'), 'A guest name')
