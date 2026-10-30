import unittest
from form_validation import normalize_digits, validate_room, validate_employee, validate_payment

class TestFormValidation(unittest.TestCase):
    def test_persian_digits(self): self.assertEqual(normalize_digits("۱۲٣"), "123")
    def test_valid_room(self): self.assertEqual(validate_room("۱۰۱", "استاندارد", 1200000), {})
    def test_invalid_room(self): self.assertIn("number", validate_room("", "استاندارد", 100))
    def test_invalid_rate(self): self.assertIn("rate", validate_room("101", "استاندارد", 0))
    def test_valid_employee(self): self.assertEqual(validate_employee("علی رضایی", "۰۹۱۲۳۴۵۶۷۸۹", 1000), {})
    def test_invalid_employee_phone(self): self.assertIn("phone", validate_employee("علی", "abc", 0))
    def test_valid_payment(self): self.assertEqual(validate_payment(1, 10000, "نقدی"), {})
    def test_invalid_payment(self): self.assertIn("amount", validate_payment(1, 0, "نقدی"))
    def test_invalid_payment_method(self): self.assertIn("method", validate_payment(1, 100, "unknown"))

if __name__ == "__main__": unittest.main()
