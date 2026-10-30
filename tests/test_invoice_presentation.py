import unittest
from invoice_presentation import render_invoice

class InvoicePresentationTests(unittest.TestCase):
    def test_english_heading(self):
        result=render_invoice([('مهمان','Ali')],'en')
        self.assertIn('Hotel invoice',result)
        self.assertIn('Guest',result)
        self.assertIn('dir="ltr"',result)
    def test_persian_heading(self):
        result=render_invoice([('مهمان','علی')],'fa')
        self.assertIn('صورتحساب هتل',result)
        self.assertIn('dir="rtl"',result)
    def test_escape_untrusted_values(self):
        result=render_invoice([('مهمان','<script>alert(1)</script>')],'en')
        self.assertNotIn('<script>',result)
        self.assertIn('&lt;script&gt;',result)
    def test_unsupported_language(self):
        with self.assertRaises(ValueError):render_invoice([], 'de')
    def test_money_not_converted(self):
        self.assertIn('1,000 toman',render_invoice([('مبلغ نهایی','1,000 toman')],'en'))
