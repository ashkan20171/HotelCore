import ast,unittest
from pathlib import Path
from datetime import date
import sqlite3
from booking_outlook_v154 import booking_outlook,outlook_summary

class BookingOutlookStage155Tests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("CREATE TABLE rooms(id INTEGER PRIMARY KEY); CREATE TABLE reservations(id INTEGER PRIMARY KEY,checkin TEXT,checkout TEXT,room_id INTEGER,status TEXT); INSERT INTO rooms VALUES(1),(2); INSERT INTO reservations VALUES(1,'2026-11-01','2026-11-10',1,'confirmed');")
    def tearDown(self):self.db.close()
    def test_7_day_horizon(self):
        rows=booking_outlook(self.db,date(2026,11,1),7)
        self.assertEqual(len(rows),7)
        self.assertEqual(rows[0]['booked_pct'],50)
    def test_90_day_horizon(self):
        self.assertEqual(len(booking_outlook(self.db,date(2026,11,1),90)),90)
    def test_threshold_changes_alerts(self):
        self.assertFalse(booking_outlook(self.db,date(2026,11,1),7,50)[0]['low_demand'])
        self.assertTrue(booking_outlook(self.db,date(2026,11,1),7,51)[0]['low_demand'])
    def test_qsettings_import_correct_module(self):
        source=Path(__file__).resolve().parents[1].joinpath('executive_dashboard_dialog_v131.py').read_text()
        tree=ast.parse(source)
        imports={}
        for node in tree.body:
            if isinstance(node,ast.ImportFrom):imports.setdefault(node.module,set()).update(alias.name for alias in node.names)
        self.assertIn('QSettings',imports['PySide6.QtCore'])
        self.assertNotIn('QSettings',imports['PySide6.QtWidgets'])
    def test_preset_default_slot(self):
        source=Path(__file__).resolve().parents[1].joinpath('executive_dashboard_dialog_v131.py').read_text()
        self.assertIn("('either','receipts','expenses','net')",source)
