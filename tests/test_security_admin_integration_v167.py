from pathlib import Path
import unittest


class SecurityAdminIntegrationV167Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path(__file__).resolve().parents[1].joinpath('main.py').read_text(encoding='utf-8')

    def test_sidebar_report_button_is_admin_only(self):
        self.assertIn("self.security_report_button.setVisible(self.role=='admin')", self.source)
        self.assertIn('self.security_report_button.clicked.connect(self.open_security_admin_report)', self.source)

    def test_report_entry_point_checks_active_session_and_permission(self):
        self.assertIn("if self.user_id is None or not getattr(self,'session_token',None):", self.source)
        self.assertIn("authorize_action(db,self.user_id,self.session_token,'security.view')", self.source)
        self.assertIn('dialog=SecurityAdminPanel(db,self.language,self)', self.source)


if __name__ == '__main__':
    unittest.main()
