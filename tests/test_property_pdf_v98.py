import tempfile, unittest
from pathlib import Path
from property_pdf import export_property_pdf
class PdfTests(unittest.TestCase):
 def test_bad_language(self):
  with self.assertRaises(ValueError):export_property_pdf('unused.pdf',[],start='2026-01-01',end='2026-01-02',language='zz')
 def test_english(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/'test.pdf'
   result=export_property_pdf(p,[dict(branch_name='Test',rooms=4,occupancy_percent=50,estimated_adr=100,estimated_revpar=50,missing_quotes=0,alerts=[])],start='2026-01-01',end='2026-01-08')
   self.assertEqual(result,1)
   self.assertTrue(p.read_bytes().startswith(b'%PDF'))
