"""Pure aggregation for permission-scoped monthly branch reports."""
from datetime import date


def merge_monthly_branches(branch_reports):
    """Sum monthly cash movements across pre-authorized branch reports.

    The caller must enforce authorization before supplying branch_reports.
    Duplicate branch names or months are rejected to prevent double counting.
    """
    totals = {}
    names = set()
    for name, rows in branch_reports:
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError('Invalid or duplicate branch')
        names.add(name)
        seen = set()
        for row in rows:
            month = row['month']
            if not isinstance(month, str) or date.fromisoformat(month+'-01').strftime('%Y-%m') != month or month in seen:
                raise ValueError('Invalid or duplicate month')
            seen.add(month)
            values = []
            for key in ('receipts', 'expenses', 'net'):
                value = row[key]
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError('Financial values must be integers')
                values.append(value)
            if values[0] < 0 or values[1] < 0 or values[2] != values[0]-values[1]:
                raise ValueError('Inconsistent cashflow')
            target = totals.setdefault(month, {'month': month, 'receipts': 0, 'expenses': 0, 'net': 0})
            for key, value in zip(('receipts', 'expenses', 'net'), values):
                target[key] += value
    return [totals[key] for key in sorted(totals)]


def trend_caption(rows, language='fa', money=str):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    net = sum(row['net'] for row in rows)
    if language == 'fa':
        return f'ماه‌های گزارش: {len(rows)} | خالص تجمیعی: {money(net)}'
    return f'Reporting months: {len(rows)} | Combined net: {money(net)}'
