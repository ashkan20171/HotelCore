import unittest
from localization import translate, NAV_FA, NAV_EN

class LocalizationTests(unittest.TestCase):
    def test_default_persian(self): self.assertEqual(translate('داشبورد'), 'داشبورد')
    def test_english(self): self.assertEqual(translate('داشبورد','en'), 'Dashboard')
    def test_all_nav(self):
        self.assertEqual(len(NAV_FA),26)
        self.assertEqual([translate(x,'en') for x in NAV_FA],NAV_EN)
    def test_nav_icon(self): self.assertEqual(translate('◈  اتاق‌ها','en'),'◈  Rooms')
    def test_unknown_data_unchanged(self): self.assertEqual(translate('مهمان شماره ۱۲۳','en'),'مهمان شماره ۱۲۳')
    def test_empty(self): self.assertEqual(translate('','en'),'')
