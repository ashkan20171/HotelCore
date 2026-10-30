import sqlite3
import unittest
from unittest.mock import patch
from report_center_v127 import record_export,list_exports

class ReportCenterTests(unittest.TestCase):
 def setUp(self):
  self.conn=sqlite3.connect(':memory:')
  self.auth=patch('report_center_v127._actor',return_value={'role':'admin'})
  self.auth.start()
 def tearDown(self):
  self.auth.stop();self.conn.close()
 def test_record_filter_search(self):
  record_export(self.conn,1,fmt='pdf',status='success',filename='/secret/folder/health.pdf',record_count=12)
  record_export(self.conn,1,fmt='xlsx',status='failed',filename='other.xlsx',error_code='filesystem')
  self.assertEqual(len(list_exports(self.conn,1)),2)
  self.assertEqual(list_exports(self.conn,1,status='success')[0][3],'health.pdf')
  self.assertEqual(len(list_exports(self.conn,1,fmt='pdf',search='HEALTH')),1)
  self.assertEqual(len(list_exports(self.conn,1,search='secret')),0)
 def test_reject_invalid(self):
  for kw in ({'fmt':'csv','status':'success','filename':'a'}, {'fmt':'pdf','status':'running','filename':'a'},
             {'fmt':'pdf','status':'success','filename':'a','record_count':True}):
   with self.assertRaises(ValueError):record_export(self.conn,1,**kw)
  with self.assertRaises(ValueError):list_exports(self.conn,1,limit=0)
  with self.assertRaises(ValueError):list_exports(self.conn,1,search='x'*101)
 def test_admin_required(self):
  self.auth.stop()
  with patch('report_center_v127._actor',side_effect=PermissionError):
   with self.assertRaises(PermissionError):list_exports(self.conn,2)
   with self.assertRaises(PermissionError):record_export(self.conn,2,fmt='pdf',status='success',filename='a.pdf')
  self.auth.start()
