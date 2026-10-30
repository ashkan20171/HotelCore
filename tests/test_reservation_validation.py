import unittest
from reservation_validation import validate_booking

class BookingValidationTests(unittest.TestCase):
    def test_valid_booking(self):
        self.assertEqual(validate_booking('علی رضایی','۰۹۱۲۳۴۵۶۷۸۹',1,'2026-10-19','2026-10-21'),{})
    def test_missing_room(self):
        self.assertIn('room',validate_booking('علی','09123456789',None,'2026-10-19','2026-10-21'))
    def test_reversed_dates(self):
        self.assertIn('dates',validate_booking('علی','09123456789',1,'2026-10-21','2026-10-19'))
    def test_invalid_date(self):
        self.assertIn('dates',validate_booking('علی','09123456789',1,'bad','2026-10-21'))
    def test_short_phone(self):
        self.assertIn('phone',validate_booking('علی','123',1,'2026-10-19','2026-10-21'))
    def test_blank_name(self):
        self.assertIn('name',validate_booking(' ','09123456789',1,'2026-10-19','2026-10-21'))
