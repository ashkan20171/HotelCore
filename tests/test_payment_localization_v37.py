import unittest
from localization import translate
from form_validation import validate_payment

class PaymentLocalizationTests(unittest.TestCase):
    def test_method_labels(self):
        self.assertEqual(translate('کارتخوان','en'), 'Card terminal')
        self.assertEqual(translate('نقدی','en'), 'Cash')
    def test_canonical_payment_methods(self):
        self.assertFalse(validate_payment(1, 1000, 'کارتخوان'))
        self.assertFalse(validate_payment(1, 1000, 'نقدی'))
    def test_guest_translation(self):
        self.assertEqual(translate('تعداد مهمانان','en'),'Guest count')
    def test_farsi_default(self):
        self.assertEqual(translate('ثبت دریافت','fa'),'ثبت دریافت')
    def test_payment_method_translation(self):
        self.assertEqual(translate('روش پرداخت','en'),'Payment method')
