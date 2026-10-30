import unittest
from localization import translate, NAV_FA, NAV_EN
class LanguageSettingsTests(unittest.TestCase):
 def test_all_navigation_translated(self):
  for fa,en in zip(NAV_FA,NAV_EN):self.assertEqual(translate(fa,'en'),en)
 def test_roundtrip_source(self):
  for fa in ('داشبورد','شناسه','تخفیف','مدیریت کدهای تخفیف'):
   self.assertEqual(translate(fa,'fa'),fa)
   self.assertNotEqual(translate(fa,'en'),fa)
 def test_untranslated_business_data_preserved(self):
  self.assertEqual(translate('Custom Guest 123','en'),'Custom Guest 123')
 def test_empty_string(self):self.assertEqual(translate('', 'en'),'')
if __name__=='__main__':unittest.main()
