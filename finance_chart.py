"""Reusable, dependency-free Qt cashflow visualization and data preparation."""
from datetime import date


def chart_points(rows):
    """Validate and normalize chronological monthly financial series."""
    result=[]
    for item in rows:
        month=str(item['month'])
        date.fromisoformat(month+'-01')
        receipts=int(item['receipts']); expenses=int(item['expenses'])
        if receipts<0 or expenses<0:
            raise ValueError('Cashflow chart requires non-negative receipts and expenses')
        result.append({'month':month,'receipts':receipts,'expenses':expenses,'net':receipts-expenses})
    if len({r['month'] for r in result})!=len(result):
        raise ValueError('Duplicate month')
    return sorted(result,key=lambda r:r['month'])


def chart_scale(rows):
    """Return a nonzero scale even for empty/all-zero datasets."""
    return max([1]+[max(r['receipts'],r['expenses']) for r in rows])


def tooltip_text(row, language='fa'):
    if language not in ('fa','en'): raise ValueError('Unsupported language')
    if language=='fa':
        return f"{row['month']}\nدریافتی: {row['receipts']:,}\nهزینه: {row['expenses']:,}\nخالص: {row['net']:,}"
    return f"{row['month']}\nReceipts: {row['receipts']:,}\nExpenses: {row['expenses']:,}\nNet: {row['net']:,}"


try:
    from PySide6.QtCore import Qt, QRectF
    from PySide6.QtGui import QColor, QPainter, QPen, QFont
    from PySide6.QtWidgets import QWidget, QToolTip
except ImportError:
    QWidget=object


class CashflowChart(QWidget):
    """Accessible, theme-aware painted chart; no QtCharts installation required."""
    def __init__(self, parent=None, language='fa'):
        if QWidget is object:
            raise RuntimeError('PySide6 is required to display the chart')
        super().__init__(parent)
        self.language=language
        self.rows=[]
        self.setMinimumHeight(245)
        self.setMouseTracking(True)
        self.setAccessibleName('روند مالی شعبه' if language=='fa' else 'Branch financial trend')

    def set_rows(self, rows):
        self.rows=chart_points(rows)
        self.setToolTip('')
        self.update()

    def _geometry(self):
        left,right,top,bottom=64,22,26,49
        width=max(1,self.width()-left-right)
        height=max(1,self.height()-top-bottom)
        return left,top,width,height

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(),QColor('#10243b'))
        left,top,width,height=self._geometry()
        p.setPen(QPen(QColor('#476079'),1))
        for tick in range(5):
            y=top+height*tick/4
            p.drawLine(int(left),int(y),int(left+width),int(y))
        p.setPen(QColor('#d9e6f2'))
        if not self.rows:
            p.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'داده‌ای برای نمایش نیست' if self.language=='fa' else 'No data for selected period')
            return
        maximum=chart_scale(self.rows)
        for tick in range(5):
            label=f'{round(maximum*(4-tick)/4):,}'
            p.drawText(QRectF(0,top+height*tick/4-9,left-8,18),Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter,label)
        n=len(self.rows);slot=width/n;bar=min(24,max(3,slot*.28))
        for index,row in enumerate(self.rows):
            center=left+(index+.5)*slot
            for offset,key,color in ((-bar*.55,'receipts','#14b8a6'),(bar*.55,'expenses','#e6a84a')):
                bar_height=height*row[key]/maximum
                p.fillRect(QRectF(center+offset-bar*.45,top+height-bar_height,bar*.9,bar_height),QColor(color))
            p.setPen(QColor('#d9e6f2'))
            p.drawText(QRectF(center-slot/2,top+height+8,slot,22),Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter,row['month'][5:])
        p.setPen(QColor('#14b8a6'));p.drawText(left,15,'● '+('دریافتی' if self.language=='fa' else 'Receipts'))
        p.setPen(QColor('#e6a84a'));p.drawText(left+125,15,'● '+('هزینه' if self.language=='fa' else 'Expenses'))

    def mouseMoveEvent(self,event):
        if not self.rows:return
        left,top,width,height=self._geometry()
        x=event.position().x()
        if x<left or x>left+width or event.position().y()<top or event.position().y()>top+height:
            QToolTip.hideText();return
        index=min(len(self.rows)-1,int((x-left)/width*len(self.rows)))
        QToolTip.showText(event.globalPosition().toPoint(),tooltip_text(self.rows[index],self.language),self)
