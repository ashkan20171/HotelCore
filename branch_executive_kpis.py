"""Permission-scoped executive KPIs derived solely from visible comparison rows."""
from branch_aggregates import visible_totals


def executive_metrics(rows):
    """Calculate cash-movement KPIs; input must already be authorized and filtered."""
    totals = visible_totals(rows)
    count = totals['branches']
    positive = sum(row['net'] > 0 for row in rows)
    negative = sum(row['net'] < 0 for row in rows)
    zero = count - positive - negative
    return {
        **totals,
        'positive_branches': positive,
        'negative_branches': negative,
        'zero_branches': zero,
        'average_net': totals['net'] / count if count else 0,
        'cash_coverage_percent': (totals['receipts'] / totals['expenses'] * 100)
        if totals['expenses'] > 0 else None,
    }


def executive_labels(metrics, language='fa', money=str):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    fa = language == 'fa'
    coverage = ('نامشخص' if fa else 'N/A') if metrics['cash_coverage_percent'] is None else f"{metrics['cash_coverage_percent']:.1f}%"
    return [
        ('شعب فیلترشده' if fa else 'Visible branches', str(metrics['branches'])),
        ('شعب با خالص مثبت' if fa else 'Positive net branches', str(metrics['positive_branches'])),
        ('شعب با خالص منفی' if fa else 'Negative net branches', str(metrics['negative_branches'])),
        ('میانگین خالص هر شعبه' if fa else 'Average net per branch', money(metrics['average_net'])),
        ('نسبت دریافتی به هزینه' if fa else 'Receipts / expenses', coverage),
    ]
