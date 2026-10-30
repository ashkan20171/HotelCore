"""In-app, dependency-free monthly cashflow trend chart for PySide6."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget, QSizePolicy
from branch_trend_data import normalize_chart_rows

SERIES = (('receipts', '#14b8a6'), ('expenses', '#f59e0b'), ('net', '#60a5fa'))




class BranchTrendChart(QWidget):
    """Responsive line chart painted with QPainter; no QtCharts dependency."""
    def __init__(self, language='fa', parent=None):
        super().__init__(parent)
        self.language = language if language in ('fa', 'en') else 'fa'
        self.rows = []
        self.setMinimumHeight(245)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, rows, language=None):
        self.rows = normalize_chart_rows(rows)
        if language in ('fa', 'en'):
            self.language = language
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor('#102235'))
        title = 'روند مالی ماهانه' if self.language == 'fa' else 'Monthly cashflow trend'
        painter.setPen(QColor('#edf5fb'))
        painter.setFont(QFont('Segoe UI', 10, QFont.Weight.DemiBold))
        painter.drawText(18, 25, title)
        if not self.rows:
            painter.setPen(QColor('#a9bac9'))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 'داده‌ای برای نمایش وجود ندارد' if self.language == 'fa' else 'No data to display')
            return
        left, right, top, bottom = 52, max(70, self.width() - 20), 48, self.height() - 42
        plot_w, plot_h = max(1, right-left), max(1, bottom-top)
        all_values = [row[key] for row in self.rows for key, _ in SERIES]
        low, high = min(0, min(all_values)), max(0, max(all_values))
        if low == high:
            high = low + 1
        padding = (high-low) * .08
        low -= padding; high += padding
        # Grid and zero axis
        for i in range(5):
            y = top + plot_h * i / 4
            painter.setPen(QPen(QColor('#2b4155'), 1))
            painter.drawLine(int(left), int(y), int(right), int(y))
        zero_y = top + (high / (high-low)) * plot_h
        painter.setPen(QPen(QColor('#6d8295'), 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(left), int(zero_y), int(right), int(zero_y))
        count = len(self.rows)
        for key, color in SERIES:
            pen = QPen(QColor(color), 2.4)
            painter.setPen(pen)
            points = []
            for index, row in enumerate(self.rows):
                x = left + (plot_w/2 if count == 1 else plot_w * index/(count-1))
                y = top + (high-row[key])/(high-low)*plot_h
                points.append(QPointF(x, y))
            for a, b in zip(points, points[1:]):
                painter.drawLine(a, b)
            painter.setBrush(QColor(color))
            for point in points:
                painter.drawEllipse(point, 3.2, 3.2)
        # Month labels, thinning labels on narrow screens.
        painter.setFont(QFont('Segoe UI', 8))
        step = max(1, (count + max(2, int(plot_w/85)) - 1) // max(2, int(plot_w/85)))
        painter.setPen(QColor('#c6d3de'))
        for index in range(0, count, step):
            x = left + (plot_w/2 if count == 1 else plot_w * index/(count-1))
            painter.drawText(QRectF(x-35, bottom+8, 70, 20), Qt.AlignmentFlag.AlignHCenter, self.rows[index]['month'])
        # Legend
        legend_y = self.height() - 10
        legend = [('receipts', 'دریافتی' if self.language == 'fa' else 'Receipts'),
                  ('expenses', 'هزینه' if self.language == 'fa' else 'Expenses'),
                  ('net', 'خالص' if self.language == 'fa' else 'Net')]
        x = left
        for key, label in legend:
            color = dict(SERIES)[key]
            painter.setPen(QPen(QColor(color), 3))
            painter.drawLine(x, legend_y-4, x+14, legend_y-4)
            painter.setPen(QColor('#edf5fb'))
            painter.drawText(x+19, legend_y, label)
            x += 100
        painter.end()
