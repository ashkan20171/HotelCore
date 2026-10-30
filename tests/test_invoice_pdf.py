import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from invoice_pdf import invoice_lines,choose_font,write_invoice_pdf

INVOICE=dict(id=7,guest='Test Guest',room='101',start='2026-10-01',end='2026-10-03',nights=2,accommodation=200,services=30,discount=10,tax=5,total=225,paid=100,balance=125)
class InvoicePdfTests(unittest.TestCase):
 def test_english_labels(self):
  lines=invoice_lines(INVOICE,'en',str,lambda x:f'{x} toman')
  self.assertIn('Guest: Test Guest',lines)
  self.assertIn('Balance: 125 toman',lines)
 def test_persian_labels(self):
  lines=invoice_lines(INVOICE,'fa',str,str)
  self.assertIn('نام مهمان: Test Guest',lines)
 def test_invalid_language(self):
  with self.assertRaises(ValueError):invoice_lines(INVOICE,'de',str,str)
 def test_missing_field(self):
  with self.assertRaises(ValueError):invoice_lines({'id':1},'en',str,str)
 def test_font_not_found(self):
  self.assertIsNone(choose_font('en',[Path('/nonexistent/ashkan-font.ttf')]))
 def test_pdf_generated(self):
  try:import reportlab
  except ImportError:self.skipTest('reportlab not installed')
  font=choose_font('en')
  if font is None:self.skipTest('No TTF font installed')
  with TemporaryDirectory() as d:
   p=Path(d)/'invoice.pdf';write_invoice_pdf(p,INVOICE,'en',str,str,font)
   self.assertTrue(p.read_bytes().startswith(b'%PDF'))
   self.assertGreater(p.stat().st_size,1000)
