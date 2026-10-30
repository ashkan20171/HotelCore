"""Accessible, bilingual finance KPI presentation; all values are recorded cash movements."""
try:
    from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
except ImportError:  # Pure KPI models remain testable without the GUI runtime.
    QFrame = object

METRICS = ('receipts', 'expenses', 'net_cash_movement')
LABELS = {'fa': ('دریافتی ثبت‌شده', 'هزینه شعبه', 'خالص گردش وجوه'),
          'en': ('Recorded receipts', 'Branch expenses', 'Net cash movement')}

def kpi_view_models(report, language='fa'):
    if language not in LABELS:
        raise ValueError('Unsupported language')
    result = []
    for key, label in zip(METRICS, LABELS[language]):
        current = int(report['current'][key]); previous = int(report['previous'][key])
        change = report['changes'][key]
        if change is not None:
            change = float(change)
        direction = 'flat' if change == 0 else ('unknown' if change is None else ('up' if change > 0 else 'down'))
        result.append(dict(key=key, label=label, current=current, previous=previous,
                           change=change, direction=direction))
    return result

class FinanceKpiCards(QFrame):
    """Compact visual KPI cards with period-on-period delta and accessible text."""
    def __init__(self, language='fa', parent=None):
        super().__init__(parent)
        self.language = language
        self.setObjectName('financeKpiPanel')
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 8, 0, 8)
        self._row.setSpacing(12)
        self._cards = []
        for _ in METRICS:
            frame = QFrame(); frame.setObjectName('financeKpiCard')
            frame.setStyleSheet('QFrame#financeKpiCard{background:#172C46;border:1px solid #29445D;border-radius:14px;padding:10px;} QLabel{color:#EAF4F8;border:0;}')
            layout = QVBoxLayout(frame)
            title = QLabel(); title.setStyleSheet('font-size:12px;color:#A9C4D1;')
            amount = QLabel(); amount.setStyleSheet('font-size:20px;font-weight:700;color:#FFFFFF;')
            delta = QLabel(); delta.setStyleSheet('font-size:12px;')
            for item in (title, amount, delta):
                item.setWordWrap(True); layout.addWidget(item)
            self._row.addWidget(frame, 1)
            self._cards.append((frame, title, amount, delta))
        self.clear()

    def clear(self):
        for frame, title, amount, delta in self._cards:
            title.setText(''); amount.setText('—'); delta.setText('')

    def set_report(self, report, format_money=str):
        for model, (frame, title, amount, delta) in zip(kpi_view_models(report, self.language), self._cards):
            title.setText(model['label']); amount.setText(format_money(model['current']))
            change = model['change']
            if change is None:
                detail = 'بدون مبنای مقایسه' if self.language == 'fa' else 'No comparison baseline'
            else:
                arrow = '▲' if change > 0 else ('▼' if change < 0 else '●')
                detail = f'{arrow} {change:+.1f}%'
            delta.setText(detail)
            color = '#94A3B8' if change is None or change == 0 else ('#3DD9B0' if (change > 0) == (model['key'] != 'expenses') else '#FFB86B')
            delta.setStyleSheet(f'color:{color};font-size:12px;font-weight:600;')
            frame.setAccessibleName(f"{model['label']}: {format_money(model['current'])}; {detail}")
