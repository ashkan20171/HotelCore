from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BookingAuditDialogStage162Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dialog_source = (ROOT / 'booking_audit_dialog_v162.py').read_text(encoding='utf-8')
        cls.main_source = (ROOT / 'main.py').read_text(encoding='utf-8')

    def test_dialog_supports_all_three_event_types(self):
        for event in ("'created'", "'updated'", "'deleted'"):
            self.assertIn(event, self.dialog_source)

    def test_filters_use_bound_sql_parameters(self):
        self.assertIn("WHERE ''' + ' AND '.join(clauses)", self.dialog_source)
        self.assertIn("execute('''SELECT id,reservation_id,event_type,event_at,actor,old_values,new_values", self.dialog_source)
        self.assertIn("params)", self.dialog_source)

    def test_before_after_snapshot_details_are_available(self):
        self.assertIn("'old_values'", self.dialog_source)
        self.assertIn("'new_values'", self.dialog_source)
        self.assertIn('json.dumps(payload, ensure_ascii=False, indent=2)', self.dialog_source)

    def test_reservations_page_opens_admin_only_audit_dialog(self):
        self.assertIn('from booking_audit_dialog_v162 import BookingAuditDialog', self.main_source)
        self.assertIn("audit_button.setVisible(self.role=='admin')", self.main_source)
        self.assertIn('dialog=BookingAuditDialog(connect,self.language,self)', self.main_source)

if __name__ == '__main__':
    unittest.main()
