import unittest
from reservation_validation import validate_booking

class BookingValidationV75(unittest.TestCase):
    def check(self, **kwargs):
        data = dict(name='Ali Reza', phone='۰۹۱۲۳۴۵۶۷۸۹', room_id=1, checkin='2026-11-01', checkout='2026-11-03')
        data.update(kwargs)
        return validate_booking(**data)
    def test_persian_digits(self): self.assertEqual(self.check(), {})
    def test_phone_reject_letters(self): self.assertIn('phone', self.check(phone='1234567abc'))
    def test_phone_accept_separators(self): self.assertNotIn('phone', self.check(phone='+49 176 12345678'))
    def test_room_reject_zero(self): self.assertIn('room', self.check(room_id=0))
    def test_room_reject_bool(self): self.assertIn('room', self.check(room_id=True))
    def test_room_reject_string(self): self.assertIn('room', self.check(room_id='1'))
    def test_name_reject_oversize(self): self.assertIn('name', self.check(name='A'*101))
    def test_dates_reject_same(self): self.assertIn('dates', self.check(checkout='2026-11-01'))
