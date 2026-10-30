"""Excel-compatible, formula-safe CSV export for branch reservations."""
import csv
from pathlib import Path

HEADERS = {
    'fa': ('شناسه رزرو', 'شماره اتاق', 'نام مهمان', 'ورود (میلادی)', 'خروج (میلادی)'),
    'en': ('Reservation ID', 'Room number', 'Guest name', 'Check-in (Gregorian)', 'Check-out (Gregorian)'),
}

def safe_cell(value):
    """Prevent spreadsheet formula execution, including leading whitespace bypasses."""
    if value is None:
        return ''
    text = str(value)
    if text.lstrip('\t\r\n ').startswith(('=', '+', '-', '@')):
        return "'" + text
    return text

def export_branch_reservations(path, rows, language='fa'):
    if language not in HEADERS:
        raise ValueError('Unsupported language')
    path = Path(path)
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADERS[language])
        for row in rows:
            if len(row) != 5:
                raise ValueError('Expected five reservation fields')
            writer.writerow([safe_cell(value) for value in row])
    return path
