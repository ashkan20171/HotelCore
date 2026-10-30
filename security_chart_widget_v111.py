"""Qt-native responsive security trend chart; no external chart dependency."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class SecurityTrendChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series = []
        self.setMinimumHeight(210)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def set_series(self, series):
        self.series = list(series)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor('#13283a'))
        width, height = self.width(), self.height()
        left, top, right, bottom = 44, 22, 18, 36
        plot_width = max(1, width-left-right)
        plot_height = max(1, height-top-bottom)
        painter.setPen(QPen(QColor('#39566b'), 1))
        for step in range(5):
            y = top + plot_height * step / 4
            painter.drawLine(left, int(y), width-right, int(y))
        if not self.series:
            painter.setPen(QColor('#b6c7d3'))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 'No data')
            return
        peak = max(1, max(row['success']+row['failure']+row['locked'] for row in self.series))
        bar_width = max(2, plot_width / len(self.series) * .68)
        colors = [('success', QColor('#19b6a1')), ('failure', QColor('#f2b455')),
                  ('locked', QColor('#ec6c75'))]
        painter.setPen(Qt.PenStyle.NoPen)
        for index, row in enumerate(self.series):
            x = left + (index+.5)*plot_width/len(self.series)-bar_width/2
            bottom_y = top+plot_height
            for key, color in colors:
                bar_height = plot_height * row[key] / peak
                painter.setBrush(color)
                painter.drawRoundedRect(int(x), int(bottom_y-bar_height), max(1,int(bar_width)),
                                        max(0,int(bar_height)), 2, 2)
                bottom_y -= bar_height
        painter.setPen(QColor('#b6c7d3'))
        painter.drawText(left, height-11, self.series[0]['date'])
        last = self.series[-1]['date']
        painter.drawText(max(left,width-right-100), height-11, last)
