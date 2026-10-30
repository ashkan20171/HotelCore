"""Validated monthly cashflow chart data, independent of Qt."""
def normalize_chart_rows(rows):
    """Validate and normalize chart rows before rendering."""
    normalized = []
    seen = set()
    for row in rows:
        month = row.get('month')
        if not isinstance(month, str) or len(month) != 7 or month[4] != '-':
            raise ValueError('Invalid month')
        try:
            year, number = int(month[:4]), int(month[5:])
        except ValueError as exc:
            raise ValueError('Invalid month') from exc
        if year < 1 or not 1 <= number <= 12 or month in seen:
            raise ValueError('Invalid or duplicate month')
        seen.add(month)
        values = []
        for key in ('receipts', 'expenses', 'net'):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('Chart amounts must be integers')
            values.append(value)
        if values[0] < 0 or values[1] < 0 or values[2] != values[0] - values[1]:
            raise ValueError('Inconsistent cashflow')
        normalized.append({'month': month, 'receipts': values[0], 'expenses': values[1], 'net': values[2]})
    return sorted(normalized, key=lambda item: item['month'])

