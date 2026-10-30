"""Accessible, dependency-free occupancy visualization for PySide6."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget

def normalized_occupancy(rows):
    """Return bounded, date-labeled occupancy series; omit undefined values."""
    result=[]
    for row in rows:
        value=row.get('occupancy_percent')
        if value is None: continue
        result.append((str(row['date']), max(0., min(100., float(value)))))
    return result

class OccupancyTrendChart(QWidget):
    def __init__(self, language='fa', parent=None):
        super().__init__(parent)
        self.language=language
        self.series=[]
        self.setMinimumHeight(210)
        self.setAccessibleName('نمودار روند اشغال' if language=='fa' else 'Occupancy trend chart')

    def set_series(self, rows):
        self.series=normalized_occupancy(rows)
        self.update()

    def paintEvent(self, event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=self.rect().adjusted(48,18,-20,-38)
        painter.fillRect(self.rect(),QColor('#F8FAFC'))
        painter.setPen(QPen(QColor('#CBD5E1'),1))
        for level in (0,25,50,75,100):
            y=rect.bottom()-rect.height()*level/100
            painter.drawLine(rect.left(),int(y),rect.right(),int(y))
            painter.setPen(QColor('#475569'))
            painter.drawText(4,int(y)-8,40,16,Qt.AlignmentFlag.AlignRight,f'{level}%')
            painter.setPen(QPen(QColor('#CBD5E1'),1))
        if not self.series:
            painter.setPen(QColor('#64748B'))
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,
                'داده‌ای برای نمایش وجود ندارد' if self.language=='fa' else 'No occupancy data')
            return
        points=[]
        n=len(self.series)
        for index,(_,value) in enumerate(self.series):
            x=rect.left()+(rect.width()*index/max(1,n-1))
            y=rect.bottom()-(rect.height()*value/100)
            points.append((int(x),int(y)))
        painter.setPen(QPen(QColor('#0F766E'),3))
        for a,b in zip(points,points[1:]):
            painter.drawLine(a[0],a[1],b[0],b[1])
        painter.setBrush(QColor('#0F766E'))
        for x,y in points:
            painter.drawEllipse(x-3,y-3,6,6)
        painter.setPen(QColor('#334155'))
        for i in sorted({0,(n-1)//2,n-1}):
            x=points[i][0]
            painter.drawText(x-38,rect.bottom()+8,76,20,Qt.AlignmentFlag.AlignHCenter,self.series[i][0][5:])
