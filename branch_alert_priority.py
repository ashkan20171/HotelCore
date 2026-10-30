"""Pure functions for categorizing and filtering already authorized cashflow alerts."""

PRIORITIES = ('all', 'critical', 'high', 'medium')


def categorize_alerts(alerts, threshold=0):
    """Assign severity by multiples of configured alert threshold.

    With zero threshold, all detected alerts are high (no useful ratio exists).
    """
    from branch_alerts import validate_threshold
    limit = validate_threshold(threshold)
    result = []
    for alert in alerts:
        amount = int(alert['amount'])
        if amount < 0:
            raise ValueError('Alert amount must not be negative')
        if limit == 0:
            severity = 'high'
        elif amount >= 3 * limit:
            severity = 'critical'
        elif amount >= 2 * limit:
            severity = 'high'
        else:
            severity = 'medium'
        result.append({**alert, 'severity': severity})
    return sorted(result, key=lambda a: ({'critical': 0, 'high': 1, 'medium': 2}[a['severity']], -a['amount'], str(a['branch_id'])))


def filter_alerts(alerts, priority='all'):
    if priority not in PRIORITIES:
        raise ValueError('Unsupported alert priority')
    return list(alerts) if priority == 'all' else [a for a in alerts if a['severity'] == priority]


def priority_label(priority, language='fa'):
    labels = {'fa': {'critical': 'بحرانی', 'high': 'مهم', 'medium': 'متوسط'},
              'en': {'critical': 'Critical', 'high': 'High', 'medium': 'Medium'}}
    if language not in labels or priority not in labels[language]:
        raise ValueError('Unsupported label')
    return labels[language][priority]
