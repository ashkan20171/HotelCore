import unittest
from reservation_edit_validation import validate_edit_dates, room_conflict

class EditValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_edit_dates('2026-10-22','2026-10-24',1),'')
    def test_equal_dates(self):
        self.assertIn('Check-out',validate_edit_dates('2026-10-22','2026-10-22',1,'en'))
    def test_reverse_dates(self):
        self.assertTrue(validate_edit_dates('2026-10-24','2026-10-22',1))
    def test_invalid_date(self):
        self.assertTrue(validate_edit_dates('2026-02-30','2026-03-01',1))
    def test_invalid_room(self):
        self.assertTrue(validate_edit_dates('2026-10-22','2026-10-24',0))
    def test_boolean_room(self):
        self.assertTrue(validate_edit_dates('2026-10-22','2026-10-24',True))
    def test_conflict(self):
        self.assertTrue(room_conflict(True))
        self.assertFalse(room_conflict(False))
