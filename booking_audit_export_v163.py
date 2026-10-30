"""Safe, deterministic CSV export for reservation audit events (Stage 163)."""
from __future__ import annotations
import csv
import json
from pathlib import Path

_FIELDS = ('id', 'reservation_id', 'event_type', 'event_at', 'actor', 'old_values', 'new_values')
_LABELS = {
    'fa': ('شناسه رویداد', 'شناسه رزرو', 'نوع رویداد', 'زمان UTC', 'عامل ثبت', 'مقادیر قبلی', 'مقادیر جدید'),
    'en': ('Event ID', 'Reservation ID', 'Event type', 'Timestamp (UTC)', 'Actor', 'Before values', 'After values'),
}

def _cell(value):
    if value is None:
        return ''
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = str(value)
    # Prevent spreadsheet formula injection for untrusted text fields.
    if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + text
    return text

def export_events_csv(path, events, language='fa'):
    """Write audit events to UTF-8-BOM CSV; return the number of exported rows.

    Expects event dictionaries as returned by booking_audit_dialog. It intentionally
    exports only the active filtered result set, not a fresh unfiltered DB query.
    """
    if language not in ('fa', 'en'):
        language = 'fa'
    target = Path(path)
    rows = list(events)
    with target.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(_LABELS[language])
        for event in rows:
            writer.writerow([_cell(event.get(field)) for field in _FIELDS])
    return len(rows)
