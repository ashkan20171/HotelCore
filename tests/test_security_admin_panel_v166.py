import csv
import os
import sqlite3
import tempfile
import unittest
from login_security import migrate_security_events, record_security_event
from security_admin_panel_v166 import security_event_report, export_security_events_csv, PYSIDE_AVAILABLE

class SecurityAdminPanelV166Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        migrate_security_events(self.db)
        record_security_event(self.db, 'alice', 'failure', '2026-10-28T10:00:00+00:00' if False else None, 'invalid_credentials')
        record_security_event(self.db, 'alice', 'locked', detail='account_locked')
        record_security_event(self.db, 'bob', 'success', detail='authenticated')

    def tearDown(self): self.db.close()

    def test_report_counts_and_limit(self):
        report = security_event_report(self.db, limit=2)
        self.assertEqual(report['shown'], 2)
        self.assertEqual(report['counts'], {'failure': 1, 'locked': 1, 'success': 1})

    def test_outcome_and_username_filters(self):
        report = security_event_report(self.db, outcome='failure', username='ali')
        self.assertEqual([e['attempted_username'] for e in report['events']], ['alice'])
        self.assertEqual(report['counts']['failure'], 1)

    def test_username_wildcards_are_literal(self):
        record_security_event(self.db, 'a_b', 'failure')
        self.assertEqual(len(security_event_report(self.db, username='a_b')['events']), 1)

    def test_date_range_validation(self):
        with self.assertRaises(ValueError): security_event_report(self.db, start='2026-10-30', end='2026-10-01')
        with self.assertRaises(ValueError): security_event_report(self.db, start='yesterday')
        with self.assertRaises(ValueError): security_event_report(self.db, limit=0)

    def test_csv_utf8_bom_and_formula_mitigation(self):
        events = [{'id': 1, 'attempted_username': '=HYPERLINK("x")', 'outcome': 'failure', 'occurred_at': '2026-10-29T00:00:00+00:00', 'detail': '+cmd'}]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'events.csv')
            export_security_events_csv(path, events, language='en')
            raw = open(path, 'rb').read()
            self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
            with open(path, encoding='utf-8-sig', newline='') as stream: rows = list(csv.reader(stream))
            self.assertEqual(rows[1][1], '\'=HYPERLINK("x")')
            self.assertEqual(rows[1][4], "'+cmd")

    def test_language_validation(self):
        with self.assertRaises(ValueError): export_security_events_csv('/tmp/never-used.csv', [], language='de')

    def test_dialog_capability_is_reported(self):
        self.assertIsInstance(PYSIDE_AVAILABLE, bool)

if __name__ == '__main__': unittest.main()
