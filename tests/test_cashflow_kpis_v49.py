import unittest
from unittest.mock import patch
from cashflow_kpis import comparison_period, percentage_change, compare_cashflow, format_comparison

class KPIComparisonTests(unittest.TestCase):
    def test_period_normal(self):
        self.assertEqual(comparison_period('2026-10-11','2026-10-21'),('2026-10-01','2026-10-11'))
    def test_period_leap_year(self):
        self.assertEqual(comparison_period('2024-03-01','2024-03-02'),('2024-02-29','2024-03-01'))
    def test_invalid_period(self):
        with self.assertRaises(ValueError): comparison_period('2026-10-21','2026-10-21')
    def test_percentage_positive(self): self.assertEqual(percentage_change(150,100),50.0)
    def test_percentage_negative(self): self.assertEqual(percentage_change(50,100),-50.0)
    def test_zero_previous(self):
        self.assertIsNone(percentage_change(50,0))
        self.assertEqual(percentage_change(0,0),0.0)
    def test_compare_authorized_scope_and_values(self):
        def fake_cashflow(conn,**kw):
            if kw['start']=='2026-10-01': return dict(receipts=100,expenses=20,net_cash_movement=80)
            return dict(receipts=200,expenses=50,net_cash_movement=150)
        with patch('cashflow_kpis.cashflow',side_effect=fake_cashflow) as fn:
            report=compare_cashflow(None,branch_id=7,user_id=2,role='manager',start='2026-10-11',end='2026-10-21')
            self.assertEqual(fn.call_count,2)
            self.assertTrue(all(c.kwargs['branch_id']==7 and c.kwargs['user_id']==2 for c in fn.call_args_list))
            self.assertEqual(report['changes']['receipts'],100.0)
            self.assertEqual(report['previous']['expenses'],20)
    def test_localized_format(self):
        r={'current':{'receipts':10,'expenses':0,'net_cash_movement':10},'previous':{'receipts':0,'expenses':0,'net_cash_movement':0},'changes':{'receipts':None,'expenses':0.0,'net_cash_movement':None}}
        self.assertEqual(format_comparison(r,'en')[0][-1],'new')
        self.assertEqual(format_comparison(r,'fa')[0][-1],'جدید')
        with self.assertRaises(ValueError):format_comparison(r,'fr')
