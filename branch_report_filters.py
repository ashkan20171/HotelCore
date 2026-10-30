"""Pure presentation filters and safe CSV export for authorized branch cashflow rows."""
import csv
import io
import unicodedata

COLUMNS = ('branch', 'receipts', 'expenses', 'net')

def filter_branches(rows, search=''):
    if not isinstance(search, str):
        raise TypeError('Search must be text')
    needle = unicodedata.normalize('NFKC', search).strip().casefold()
    return [row for row in rows if needle in unicodedata.normalize('NFKC', str(row['branch'])).casefold()]

def comparison_csv(rows, language='fa'):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    headings = ('شعبه', 'دریافتی', 'هزینه', 'خالص گردش وجوه') if language == 'fa' else ('Branch', 'Receipts', 'Expenses', 'Net cash movement')
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer)
    writer.writerow(headings)
    for row in rows:
        writer.writerow([safe_csv_cell(row['branch']), int(row['receipts']), int(row['expenses']), int(row['net'])])
    return '\ufeff' + buffer.getvalue()

def safe_csv_cell(value):
    """Prevent spreadsheet formula interpretation of untrusted branch names."""
    text = str(value)
    if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r', '\n')):
        return "'" + text
    return text
