import unittest,tempfile
from pathlib import Path
from executive_dashboard_export_v133 import _pdf_font,export_pdf
from test_executive_dashboard_export_v133 import DATA
class UnicodePdfTests(unittest.TestCase):
 def test_font(self):self.assertIsInstance(_pdf_font(),str)
 def test_persian_room_name(self):
  with tempfile.TemporaryDirectory() as d:
   data=dict(DATA,room_types=[dict(DATA['room_types'][0],type='سوئیت')])
   p=Path(d)/'persian.pdf';export_pdf(data,p)
   self.assertTrue(p.read_bytes().startswith(b'%PDF'))
