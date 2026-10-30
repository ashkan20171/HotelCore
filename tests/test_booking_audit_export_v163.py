import csv
import tempfile
import unittest
from pathlib import Path
from booking_audit_export_v163 import export_events_csv

class BookingAuditExportStage163Tests(unittest.TestCase):
    def test_exports_filtered_events_with_localized_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'audit.csv'
            count = export_events_csv(path, [{'id': 4, 'reservation_id': 12, 'event_type': 'updated',
                'event_at': '2026-10-24T10:00:00Z', 'actor': 'database-trigger',
                'old_values': {'status': 'reserved'}, 'new_values': {'status': 'checked-in'}}], 'en')
            self.assertEqual(count, 1)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows[0][0], 'Event ID')
            self.assertEqual(rows[1][0], '4')
            self.assertIn('status', rows[1][5])

    def test_empty_export_still_has_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'audit.csv'
            self.assertEqual(export_events_csv(path, [], 'fa'), 0)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 'شناسه رویداد')

    def test_formula_injection_is_neutralized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'audit.csv'
            export_events_csv(path, [{'actor': '=HYPERLINK("bad")'}], 'en')
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows[1][4], "'=HYPERLINK(\"bad\")")

if __name__ == '__main__':
    unittest.main()
