"""Presentation helpers for branch cash movement (not accrual profit)."""

def cashflow_cards(report, language='fa'):
    if language not in ('fa','en'):
        raise ValueError('Unsupported language')
    receipts=int(report['receipts']); expenses=int(report['expenses'])
    if receipts<0 or expenses<0:
        raise ValueError('Negative totals are invalid')
    net=receipts-expenses
    labels=('دریافتی ثبت‌شده','هزینه شعبه','خالص گردش وجوه') if language=='fa' else ('Recorded receipts','Branch expenses','Net cash movement')
    return [(labels[0],receipts),(labels[1],expenses),(labels[2],net)]

def cashflow_comparison(reports,language='fa'):
    if language not in ('fa','en'):
        raise ValueError('Unsupported language')
    result=[]
    for name, report in reports:
        cards=cashflow_cards(report,language)
        result.append({'branch':name,'receipts':cards[0][1],'expenses':cards[1][1],'net':cards[2][1]})
    return sorted(result,key=lambda r:(-r['net'],r['branch']))
