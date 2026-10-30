import unittest
from branch_alert_priority import categorize_alerts, filter_alerts, priority_label

class AlertPriorityTests(unittest.TestCase):
    def setUp(self):
        self.alerts=[{'branch_id':1,'kind':'decline','amount':100}, {'branch_id':2,'kind':'negative','amount':200}, {'branch_id':3,'kind':'decline','amount':300}]
    def test_medium(self):self.assertEqual(categorize_alerts(self.alerts,100)[2]['severity'],'medium')
    def test_high(self):self.assertEqual(categorize_alerts(self.alerts,100)[1]['severity'],'high')
    def test_critical(self):self.assertEqual(categorize_alerts(self.alerts,100)[0]['severity'],'critical')
    def test_zero_threshold(self):self.assertTrue(all(a['severity']=='high' for a in categorize_alerts(self.alerts,0)))
    def test_filter(self):self.assertEqual(len(filter_alerts(categorize_alerts(self.alerts,100),'critical')),1)
    def test_all(self):self.assertEqual(len(filter_alerts(categorize_alerts(self.alerts,100))),3)
    def test_invalid_filter(self):
        with self.assertRaises(ValueError):filter_alerts([], 'unknown')
    def test_negative_amount(self):
        with self.assertRaises(ValueError):categorize_alerts([{'amount':-1}],1)
    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):categorize_alerts([], -1)
    def test_persian_label(self):self.assertEqual(priority_label('critical','fa'),'بحرانی')
    def test_english_label(self):self.assertEqual(priority_label('medium','en'),'Medium')
    def test_does_not_mutate(self):
        categorize_alerts(self.alerts,100)
        self.assertNotIn('severity',self.alerts[0])
