import sqlite3
import unittest
from executive_alert_settings_v135 import DEFAULTS,load,save,validate
from executive_occupancy_v134 import management_alerts

class AlertPreferencesTests(unittest.TestCase):
    def setUp(self):self.conn=sqlite3.connect(':memory:')
    def tearDown(self):self.conn.close()
    def test_default_without_migration(self):self.assertEqual(load(self.conn,1),DEFAULTS)
    def test_save_and_isolation(self):
        settings={'low_occupancy':40,'high_expense_ratio':80,'receipts_decline':15}
        save(self.conn,1,settings)
        self.assertEqual(load(self.conn,1),settings)
        self.assertEqual(load(self.conn,2),DEFAULTS)
    def test_update(self):
        save(self.conn,1,DEFAULTS)
        save(self.conn,1,{'low_occupancy':5,'high_expense_ratio':70,'receipts_decline':10})
        self.assertEqual(load(self.conn,1)['low_occupancy'],5)
    def test_invalid_values(self):
        for bad in (-1,101,True,3.5,'50'):
            with self.assertRaises(ValueError):validate(dict(DEFAULTS,low_occupancy=bad))
    def test_invalid_actor(self):
        with self.assertRaises(ValueError):save(self.conn,0,DEFAULTS)
    def test_custom_decline(self):
        current={'income':85,'expenses':0,'room_count':1,'occupancy_pct':80}
        previous={'income':100}
        self.assertIn('receipts_decline',management_alerts(current,previous,receipts_decline=10))
        self.assertNotIn('receipts_decline',management_alerts(current,previous,receipts_decline=20))
if __name__=='__main__':unittest.main()
