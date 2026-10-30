"""Pure geometry and accessibility helpers for financial charts."""
from math import isfinite

def nearest_category(x, width, count, left=30, right_margin=18):
    """Return zero-based category index inside plot, or None outside it."""
    if type(count) is not int or count < 1 or not all(type(v) in (int,float) and isfinite(v) for v in (x,width,left,right_margin)):
        return None
    span=width-left-right_margin
    if span<=0 or x<left or x>width-right_margin:return None
    return min(count-1,max(0,int((x-left)/span*count)))

def chart_tooltip(record, fa=False, kind='monthly'):
    """Localizable hover text; do not reinterpret recorded cash flow as profit."""
    if kind=='monthly':
        month=record['month'];income=record['income'];expenses=record['expenses']
        return (f'ماه: {month}\nدریافتی: {income:,.0f}\nهزینه: {expenses:,.0f}\nاختلاف: {income-expenses:,.0f}' if fa else
                f'Month: {month}\nReceipts: {income:,.0f}\nExpenses: {expenses:,.0f}\nCash difference: {income-expenses:,.0f}')
    if kind=='yoy':
        key=record['key'];names={'income':('دریافتی','Receipts'),'expenses':('هزینه','Expenses'),'difference':('اختلاف','Cash difference')}
        name=names[key][0 if fa else 1]
        return (f'{name}\nدوره جاری: {record["current"]:,.0f}\nسال قبل: {record["previous"]:,.0f}' if fa else
                f'{name}\nCurrent period: {record["current"]:,.0f}\nPrevious year: {record["previous"]:,.0f}')
    raise ValueError('Unsupported chart type')

def responsive_chart_height(width, base=190, minimum=140, maximum=290):
    if type(width) not in (int,float) or not isfinite(width):raise ValueError('Invalid width')
    return max(minimum,min(maximum,round(base + (width-850)*0.12)))
