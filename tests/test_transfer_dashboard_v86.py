import unittest
from transfer_dashboard import build_transfer_dashboard

class TransferDashboardTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(build_transfer_dashboard([])['total'],0)
    def test_monthly_and_source(self):
        rows=[(1,'2026-10-01',5,101,102,'alice'),(2,'2026-10-02',6,101,103,'alice'),(3,'2026-09-02',7,103,101,'bob')]
        result=build_transfer_dashboard(rows)
        self.assertEqual(result['monthly'], [('2026-09',1),('2026-10',2)])
        self.assertEqual(result['sources'][0],('101',2))
        self.assertEqual(result['actors'][0],('alice',2))
    def test_limit(self):
        rows=[(1,'2026-10-01',1,1,2,'a'),(2,'2026-10-01',2,2,3,'b')]
        self.assertEqual(len(build_transfer_dashboard(rows,limit=1)['actors']),1)
    def test_invalid_limit(self):
        for value in (0,-1,True,'1'):
            with self.subTest(value=value),self.assertRaises(ValueError):build_transfer_dashboard([],limit=value)
