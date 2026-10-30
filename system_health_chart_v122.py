"""Accessible Qt-native health chart with hover tooltips and threshold indicator."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class HealthTrendChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.series = []
        self.threshold = 20
        self.language = 'en'
        self.setMinimumHeight(205)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def set_series(self, series, threshold=20, language='en'):
        self.series = list(series)
        self.threshold = max(0, min(100, int(threshold)))
        self.language = language
        self.setToolTip('')
        self.update()

    def mouseMoveEvent(self, event):
        if not self.series:
            self.setToolTip(''); return
        width = max(1, self.width() - 66)
        index = int((event.position().x() - 45) / width * len(self.series))
        if 0 <= index < len(self.series):
            row = self.series[index]
            self.setToolTip(f"{row['date']} | {row['checks']} checks | {row['warnings']} warnings")
        else:
            self.setToolTip('')

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor('#13283a'))
        w,h = self.width(),self.height()
        left,top,right,bottom = 45,20,21,39
        pw,ph = max(1,w-left-right),max(1,h-top-bottom)
        for percent in (0,25,50,75,100):
            y = int(top + ph * (100-percent)/100)
            p.setPen(QPen(QColor('#355268'),1))
            p.drawLine(left,y,w-right,y)
            p.setPen(QColor('#b7ced9'))
            p.drawText(3,y+4,f'{percent}%')
        y = int(top + ph * (100-self.threshold)/100)
        p.setPen(QPen(QColor('#fbbf24'),2,Qt.PenStyle.DashLine))
        p.drawLine(left,y,w-right,y)
        if not self.series:
            p.setPen(QColor('#b7ced9'))
            p.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'داده‌ای موجود نیست' if self.language=='fa' else 'No health checks')
            return
        bar = max(1, int(pw/len(self.series)*.68))
        p.setPen(Qt.PenStyle.NoPen)
        for i,row in enumerate(self.series):
            x = int(left+(i+.5)*pw/len(self.series)-bar/2)
            if row['checks'] == 0: continue
            rate = row['warnings']*100/row['checks']
            color = QColor('#ef777c') if rate >= self.threshold and row['warnings'] else QColor('#2dd4bf')
            p.setBrush(color)
            height = max(1,int(ph*rate/100))
            p.drawRoundedRect(x,top+ph-height,bar,height,2,2)
        p.setPen(QColor('#b7ced9'))
        p.drawText(left,h-12,self.series[0]['date'])
        p.drawText(max(left,w-right-102),h-12,self.series[-1]['date'])
