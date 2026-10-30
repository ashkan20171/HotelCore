import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from transfer_pdf_report import shape_pdf_text, find_unicode_font, export_transfers_pdf

def rtl_available():
    try:
        import arabic_reshaper
        import bidi
        return True
    except ImportError:
        return False

class TransferPdfV85Tests(unittest.TestCase):
    def test_escape_english(self):
        self.assertEqual(shape_pdf_text('<Guest & Co>', 'en'), '&lt;Guest &amp; Co&gt;')
    @unittest.skipUnless(rtl_available(), "RTL shaping dependencies unavailable")
    def test_persian_shaping(self):
        self.assertTrue(shape_pdf_text('انتقال اتاق', 'fa'))
    def test_pdf_english(self):
        with TemporaryDirectory() as d:
            target=Path(d)/'report.pdf'
            stats=export_transfers_pdf(target, [(1,'2026-10-22','14','101','205','admin')],language='en')
            self.assertEqual(stats['total'],1)
            self.assertTrue(target.read_bytes().startswith(b'%PDF'))
    @unittest.skipUnless(rtl_available(), "RTL shaping dependencies unavailable")
    def test_pdf_persian(self):
        if not find_unicode_font():self.skipTest('Unicode TTF unavailable')
        with TemporaryDirectory() as d:
            target=Path(d)/'report-fa.pdf'
            export_transfers_pdf(target, [(1,'2026-10-22','14','101','205','اشکان')],language='fa')
            self.assertTrue(target.read_bytes().startswith(b'%PDF'))
