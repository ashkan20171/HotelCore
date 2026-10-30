import sqlite3
import unittest
from unittest.mock import patch
from report_preferences_v128 import save_preset,list_presets,delete_preset

class PresetTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.auth=patch('report_preferences_v128._actor',return_value={'role':'admin'})
  self.auth.start()
 def tearDown(self):
  self.auth.stop();self.db.close()
 def test_round_trip_and_isolation(self):
  save_preset(self.db,1,'Weekly',7,20)
  save_preset(self.db,1,'Weekly',14,35)
  self.assertEqual(list_presets(self.db,1),[('Weekly',14,35)])
  self.assertEqual(list_presets(self.db,2),[])
  self.assertFalse(delete_preset(self.db,2,'Weekly'))
  self.assertTrue(delete_preset(self.db,1,'Weekly'))
  self.assertEqual(list_presets(self.db,1),[])
 def test_validation(self):
  for name,days,threshold in [('bad/name',7,20),('x',0,20),('x',7,101),('x',True,20),(' ',7,20)]:
   with self.assertRaises(ValueError):save_preset(self.db,1,name,days,threshold)
 def test_limit(self):
  for n in range(20):save_preset(self.db,1,'p'+str(n),7,20)
  with self.assertRaises(ValueError):save_preset(self.db,1,'extra',7,20)
  save_preset(self.db,1,'p0',8,25)
 def test_authorization(self):
  self.auth.stop()
  with patch('report_preferences_v128._actor',side_effect=PermissionError):
   with self.assertRaises(PermissionError):list_presets(self.db,1)
  self.auth.start()
