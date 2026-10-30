"""Filter already-authorized branch comparison rows without database access."""
from decimal import Decimal, InvalidOperation

METRICS = ('receipts', 'expenses', 'net')
STATES = ('all', 'positive', 'negative', 'zero')

def filter_financial_rows(rows, *, metric='net', minimum=None, maximum=None, state='all'):
    if metric not in METRICS:
        raise ValueError('Unsupported metric')
    if state not in STATES:
        raise ValueError('Unsupported state')
    def parse(value):
        if value is None or value == '':
            return None
        try:
            number = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise ValueError('Invalid financial bound') from None
        if not number.is_finite():
            raise ValueError('Financial bound must be finite')
        return number
    low, high = parse(minimum), parse(maximum)
    if low is not None and high is not None and low > high:
        raise ValueError('Minimum cannot exceed maximum')
    output=[]
    for row in rows:
        value=Decimal(str(row[metric]))
        if low is not None and value < low: continue
        if high is not None and value > high: continue
        if state == 'positive' and value <= 0: continue
        if state == 'negative' and value >= 0: continue
        if state == 'zero' and value != 0: continue
        output.append(row)
    return output
