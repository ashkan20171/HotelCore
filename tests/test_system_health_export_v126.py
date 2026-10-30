import os
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from system_health_export_v126 import export_report, ExportCancelled

class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'hotel.db'
        sqlite3.connect(self.db).close()
        self.target=Path(self.tmp.name)/'report.xlsx'
        self.auth=patch('system_health_export_v126.authorize_action')
        self.auth.start()
        self.addCleanup(self.auth.stop)

    def test_success_and_progress(self):
        progress=[]
        result=export_report(self.db,1,'token',self.target,'xlsx',language='en',
            progress=progress.append,writer=lambda p,c,a,language: (Path(p).write_bytes(b'xlsx') and 2))
        self.assertEqual(result,2)
        self.assertEqual(self.target.read_bytes(),b'xlsx')
        self.assertEqual(progress,[5,25,85,100])

    def test_cancel_preserves_existing(self):
        self.target.write_bytes(b'old')
        flag=threading.Event()
        def renderer(p,c,a,language):
            Path(p).write_bytes(b'partial')
            flag.set()
            return 1
        with self.assertRaises(ExportCancelled):
            export_report(self.db,1,'token',self.target,'xlsx',cancel_event=flag,writer=renderer)
        self.assertEqual(self.target.read_bytes(),b'old')
        self.assertFalse(any(Path(self.tmp.name).glob('.hotel_health_*')))

    def test_error_preserves_existing(self):
        self.target.write_bytes(b'old')
        def broken(*args,**kwargs):raise OSError('disk full')
        with self.assertRaises(OSError):
            export_report(self.db,1,'token',self.target,'xlsx',writer=broken)
        self.assertEqual(self.target.read_bytes(),b'old')
        self.assertFalse(any(Path(self.tmp.name).glob('.hotel_health_*')))

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):
            export_report(self.db,1,'token',self.target,'csv')

    def test_pre_cancel_does_not_create_file(self):
        flag=threading.Event();flag.set()
        with self.assertRaises(ExportCancelled):
            export_report(self.db,1,'token',self.target,'xlsx',cancel_event=flag)
        self.assertFalse(self.target.exists())

    def test_authorization_required(self):
        with patch('system_health_export_v126.authorize_action',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                export_report(self.db,1,'token',self.target,'xlsx')
        self.assertFalse(self.target.exists())

if __name__=='__main__':unittest.main()
