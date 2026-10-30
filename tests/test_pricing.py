import unittest
from pricing import calculate_stay

class PricingTests(unittest.TestCase):
    def test_base(self):
        total, rows = calculate_stay(1000,'استاندارد','2026-10-20','2026-10-22',[])
        self.assertEqual(total,2000)
        self.assertEqual(len(rows),2)
    def test_seasonal(self):
        rules=[('همه','2026-10-21','2026-10-23',150)]
        self.assertEqual(calculate_stay(1000,'استاندارد','2026-10-20','2026-10-23',rules)[0],4000)
    def test_checkout_exclusive(self):
        self.assertEqual(calculate_stay(1000,'سوئیت','2026-10-20','2026-10-21',[('همه','2026-10-21','2026-10-23',200)])[0],1000)
    def test_invalid(self):
        with self.assertRaises(ValueError): calculate_stay(1000,'سوئیت','2026-10-21','2026-10-21',[])
