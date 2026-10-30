import csv,sqlite3,tempfile,unittest
from datetime import date
from pathlib import Path
from booking_cancellation_types_v160 import cancellation_by_room_type,export_cancellation_csv
class CancellationTypeTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""CREATE TABLE rooms(id INTEGER PRIMARY KEY,kind TEXT);
        CREATE TABLE reservations(id INTEGER PRIMARY KEY,room_id INTEGER,created_at TEXT,status TEXT);
        INSERT INTO rooms VALUES(1,'Deluxe'),(2,'Standard'),(3,'=BAD');
        INSERT INTO reservations VALUES(1,1,'2026-10-20','confirmed'),(2,1,'2026-10-21','cancelled'),
        (3,2,'2026-10-21','لغو شده'),(4,3,'2026-10-22','confirmed'),(5,2,'2026-09-01','cancelled');""")
    def tearDown(self):self.db.close()
    def test_counts_and_dates(self):
        rows=cancellation_by_room_type(self.db,date(2026,10,23),7)
        d={r['room_type']:r for r in rows}
        self.assertEqual(d['Deluxe']['gross'],2)
        self.assertEqual(d['Deluxe']['cancelled_pct'],50.0)
        self.assertEqual(d['Standard']['net'],0)
        self.assertEqual(sum(r['gross'] for r in rows),4)
    def test_empty_and_bounds(self):
        self.assertEqual(cancellation_by_room_type(self.db,date(2026,11,23),7),[])
        with self.assertRaises(ValueError):cancellation_by_room_type(self.db,date.today(),91)
    def test_export_escapes_formulas(self):
        rows=cancellation_by_room_type(self.db,date(2026,10,23),7)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'report.csv';export_cancellation_csv(p,rows)
            with p.open(encoding='utf-8-sig',newline='') as f: data=list(csv.reader(f))
            self.assertTrue(any(r[0]=="'=BAD" for r in data[1:]))
            self.assertEqual(len(data),4)
if __name__=='__main__':unittest.main()
