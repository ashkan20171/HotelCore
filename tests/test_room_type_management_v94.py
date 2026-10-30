import unittest
import tempfile
from pathlib import Path
from room_type_management import ranked_room_types, room_type_risks, export_room_type_ranking_csv

ROWS=[
 {'kind':'Standard','estimated_revpar':100,'estimated_adr':140,'occupancy_percent':35,'estimated_value':500,'missing_quotes':2},
 {'kind':'Suite','estimated_revpar':None,'estimated_adr':None,'occupancy_percent':70,'estimated_value':0,'missing_quotes':0},
 {'kind':'Deluxe','estimated_revpar':200,'estimated_adr':250,'occupancy_percent':80,'estimated_value':800,'missing_quotes':0},
]
class RoomTypeManagementTests(unittest.TestCase):
 def test_revpar_rank(self): self.assertEqual([r['kind'] for r in ranked_room_types(ROWS)],['Deluxe','Standard','Suite'])
 def test_occupancy_rank(self): self.assertEqual(ranked_room_types(ROWS,'occupancy_percent')[0]['kind'],'Deluxe')
 def test_invalid_metric(self):
  with self.assertRaises(ValueError): ranked_room_types(ROWS,'password')
 def test_risks(self):
  self.assertEqual({r[1] for r in room_type_risks(ROWS,low_occupancy=40)}, {'low_occupancy','missing_quotes'})
 def test_csv(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'r.csv'
   self.assertEqual(export_room_type_ranking_csv(path,ROWS),3)
   self.assertIn('Deluxe',path.read_text(encoding='utf-8-sig'))
 def test_bad_threshold(self):
  with self.assertRaises(ValueError): room_type_risks(ROWS,low_occupancy=101)
