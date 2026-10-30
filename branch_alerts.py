"""Pure, permission-scoped branch cashflow alert rules.

Inputs must already have been restricted to authorized branches. Alerts are
informational and do not represent accrual profit/loss.
"""

def validate_threshold(value):
    if isinstance(value, bool):
        raise ValueError('Threshold must be a non-negative integer')
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError('Threshold must be a non-negative integer') from exc
    if number < 0 or str(value).strip() not in (str(number),):
        raise ValueError('Threshold must be a non-negative integer')
    return number


def evaluate_alerts(insights, threshold=0):
    """Alert for negative current net below threshold or deterioration >= threshold.

    A threshold of zero detects any negative current net or any decline.
    """
    limit = validate_threshold(threshold)
    alerts = []
    for item in insights:
        net = int(item['net'])
        change = int(item['change'])
        if net < 0 and abs(net) > limit:
            alerts.append({'branch_id': item['branch_id'], 'kind': 'negative',
                           'amount': abs(net), 'net': net})
        if change < 0 and abs(change) > limit:
            alerts.append({'branch_id': item['branch_id'], 'kind': 'decline',
                           'amount': abs(change), 'net': net})
    return sorted(alerts, key=lambda alert: (-alert['amount'], str(alert['branch_id']), alert['kind']))


def alert_summary(alerts, language='fa'):
    if language not in ('fa', 'en'):
        raise ValueError('Unsupported language')
    negative = sum(item['kind'] == 'negative' for item in alerts)
    decline = sum(item['kind'] == 'decline' for item in alerts)
    if language == 'fa':
        return f'هشدار خالص منفی: {negative}  |  هشدار افت نسبت به دوره قبل: {decline}'
    return f'Negative net alerts: {negative}  |  Period decline alerts: {decline}'
