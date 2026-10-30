"""Bilingual executive overview; SQLite queries run in a separate Qt worker."""
import sqlite3
from PySide6.QtCore import Qt,QThread,Signal,QSettings
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QSpinBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QProgressBar,QTabWidget,QWidget,QFileDialog,QMessageBox,QScrollArea,QGridLayout,QFrame,QSizePolicy,QGroupBox,QLineEdit,QAbstractItemView,QComboBox,QCheckBox,QDateEdit
from PySide6.QtGui import QPainter,QPen,QColor
from PySide6.QtCore import QRectF
from executive_chart_tooltips_v138 import nearest_point
from executive_chart_interaction_v150 import nearest_category,chart_tooltip,responsive_chart_height
from executive_jalali_v143 import jalali_label,parse_jalali
from executive_db_connection_v140 import open_dashboard_db
from executive_kpi_presentation_v137 import compare_periods, responsive_columns
from operation_guard import authorize_action
from executive_dashboard_v131 import snapshot
from room_revenue_analytics_v132 import room_value_by_type
from executive_occupancy_v134 import daily_occupancy,management_alerts
from datetime import date
from booking_outlook_v154 import booking_outlook,outlook_summary
from booking_calendar_v156 import calendar_weeks,coverage_band,coverage_insights
from booking_management_v157 import weekly_coverage,export_booking_excel,export_booking_pdf
from booking_pace_v158 import booking_pace,pace_alerts
from booking_pace_insights_v159 import creation_cohorts,cohort_alerts
from booking_cancellation_types_v160 import cancellation_by_room_type,export_cancellation_csv
from executive_alert_settings_v135 import load as load_alert_settings, save as save_alert_settings, DEFAULTS
from executive_yoy_v147 import year_over_year_calendar

class ExecutiveWorker(QThread):
    succeeded=Signal(object)
    failed=Signal(str)
    def __init__(self,path,actor,token,days,parent=None,start_date=None,end_date=None,fa=False,history_years=4,outlook_days=30,outlook_threshold=30,pace_min=1,pace_decline=25,pace_cancel=30):
        super().__init__(parent)
        self.path=path;self.actor=actor;self.token=token;self.days=days;self.start_date=start_date;self.end_date=end_date;self.fa=fa;self.history_years=history_years;self.outlook_days=outlook_days;self.outlook_threshold=outlook_threshold;self.pace_min=pace_min;self.pace_decline=pace_decline;self.pace_cancel=pace_cancel
    def run(self):
        try:
            if self.isInterruptionRequested():return
            with open_dashboard_db(self.path,read_only=True) as conn:
                authorize_action(conn,self.actor,self.token,'security.view')
                if self.isInterruptionRequested():return
                result=snapshot(conn,self.actor,days=self.days,start_date=self.start_date,end_date=self.end_date)
                from executive_multiyear_v151 import historical_cashflow
                result['multi_year']=historical_cashflow(conn,date.fromisoformat(result['start']),date.fromisoformat(result['end']),calendar='jalali' if self.fa else 'gregorian',years=self.history_years)
                result['yoy']=year_over_year_calendar(conn,date.fromisoformat(result['start']),date.fromisoformat(result['end']),result['current'],'jalali' if self.fa else 'gregorian')
                result["room_types"]=room_value_by_type(conn,date.fromisoformat(result["start"]),date.fromisoformat(result["end"]))
                result["occupancy_series"]=daily_occupancy(conn,date.fromisoformat(result["start"]),date.fromisoformat(result["end"]))
                result["booking_outlook"]=booking_outlook(conn,date.today(),days=self.outlook_days,low_threshold=self.outlook_threshold)
                result["booking_pace"]=booking_pace(conn,date.today(),days=self.outlook_days)
                result["booking_cohorts"]=creation_cohorts(conn,date.today(),days=self.outlook_days)
                result["cancellation_by_type"]=cancellation_by_room_type(conn,date.today(),days=self.outlook_days)
                settings=load_alert_settings(conn,self.actor)
                result["alert_settings"]=settings
                result["alerts"]=management_alerts(result["current"],result["previous"],**settings)
            if not self.isInterruptionRequested():self.succeeded.emit(result)
        except (sqlite3.Error,PermissionError,ValueError):
            if not self.isInterruptionRequested():self.failed.emit('Unable to load authorized dashboard data')

class BookingPaceChart(QWidget):
    """Gross and net creation cohorts, based on current cancellation status."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent);self.fa=fa;self.rows=[];self.setMinimumHeight(190);self.setMouseTracking(True)
    def set_rows(self,rows):self.rows=list(rows);self.update()
    def mouseMoveEvent(self,event):
        i=nearest_category(event.position().x(),self.width(),len(self.rows),left=38,right_margin=16)
        if i is not None and i<len(self.rows):
            r=self.rows[i];self.setToolTip(f"{r['date']}\nGross: {r['gross']} | Net: {r['net']} | Cancelled: {r['cancelled']}")
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        area=self.rect().adjusted(38,16,-16,-30)
        if not self.rows or area.width()<=0 or area.height()<=0:return
        top=max(1,max(r['gross'] for r in self.rows));step=area.width()/len(self.rows)
        for i,r in enumerate(self.rows):
            x=area.left()+i*step
            for key,offset,color in [('gross',.1,'#F3B565'),('net',.5,'#3DD6BD')]:
                height=area.height()*r[key]/top
                painter.fillRect(QRectF(x+step*offset,area.bottom()-height,max(1,step*.35),height),QColor(color))
        painter.setPen(QColor('#D9E9F0'))
        painter.drawText(area.left(),self.height()-7,self.rows[0]['date'])
        painter.drawText(max(area.left(),self.width()-105),self.height()-7,self.rows[-1]['date'])

class BookingCoverageChart(QWidget):
    """Actual booked coverage by future date; no statistical forecasting."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent)
        self.fa=fa;self.rows=[];self.setMinimumHeight(210);self.setMouseTracking(True)
    def set_rows(self,rows):
        self.rows=list(rows);self.update()
    def mouseMoveEvent(self,event):
        from executive_chart_interaction_v150 import nearest_category
        i=nearest_category(event.position().x(),self.width(),len(self.rows),42,16)
        if i is not None:
            row=self.rows[i]
            self.setToolTip(f"{row['date']}\n{row['booked_rooms']}/{row['total_rooms']} — {row['booked_pct']}%")
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        area=self.rect().adjusted(42,18,-16,-36)
        if area.width()<1 or area.height()<1:return
        painter.setPen(QColor('#607E92'))
        for pct in (0,50,100):
            y=area.bottom()-round(area.height()*pct/100)
            painter.drawLine(area.left(),y,area.right(),y)
            painter.drawText(3,y+4,str(pct)+'%')
        if not self.rows:return
        step=area.width()/len(self.rows)
        for i,row in enumerate(self.rows):
            height=area.height()*max(0,min(100,float(row['booked_pct'])))/100
            painter.fillRect(QRectF(area.left()+step*(i+.16),area.bottom()-height,max(1,step*.68),height),QColor('#F3B565' if row['low_demand'] else '#3DD6BD'))
        painter.setPen(QColor('#D9E9F0'))
        painter.drawText(area.left(),self.height()-8,self.rows[0]['date'])
        painter.drawText(max(area.left(),self.width()-105),self.height()-8,self.rows[-1]['date'])

class RoomPerformanceChart(QWidget):
    """Accessible, dependency-free room-type metric comparison chart."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent)
        self.fa=fa;self.rows=[];self.metric='estimated_revpar'
        self.setMinimumHeight(210);self.setMouseTracking(True)
    def set_rows(self,rows,metric):
        from room_performance_v153 import performance_rows
        self.rows=performance_rows(rows,metric);self.metric=metric;self.update()
    def mouseMoveEvent(self,event):
        if self.rows:
            index=nearest_category(event.position().x(),self.width(),len(self.rows),left=38,right_margin=14)
            if index is not None and 0<=index<len(self.rows):
                row=self.rows[index]
                self.setToolTip(f"{row['type']}\n{self.metric}: {row[self.metric]:,.2f}")
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        area=self.rect().adjusted(38,18,-14,-45)
        if area.width()<1 or area.height()<1:return
        painter.setPen(QColor('#7793A5'));painter.drawLine(area.left(),area.bottom(),area.right(),area.bottom())
        if not self.rows:return
        maximum=max(1,max(row[self.metric] for row in self.rows))
        step=area.width()/len(self.rows)
        for i,row in enumerate(self.rows):
            x=area.left()+step*(i+.5)
            height=row[self.metric]/maximum*area.height()
            painter.fillRect(QRectF(x-min(14,step*.3),area.bottom()-height,min(28,step*.6),height),QColor('#3DD6BD'))
            painter.setPen(QColor('#E2F2F8'))
            painter.drawText(QRectF(x-step*.48,area.bottom()+4,step*.96,35),Qt.AlignmentFlag.AlignCenter,str(row['type'])[:12])

class MultiYearTrendChart(QWidget):
    """Five-period historical comparison; mouse hover shows recorded amounts."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent)
        self.fa=fa;self.points=[];self.setMinimumHeight(205);self.setMouseTracking(True)
    def set_rows(self,rows):
        from executive_multiyear_trends_v152 import historical_trends
        self.points=historical_trends(rows) if rows else []
        self.update()
    def mouseMoveEvent(self,event):
        from executive_chart_interaction_v150 import nearest_category
        if self.points:
            index=nearest_category(event.position().x(),self.width(),len(self.points),left=42,right_margin=18)
            if index is not None and 0<=index<len(self.points):
                item=self.points[index]
                labels=('دریافتی','هزینه','اختلاف') if self.fa else ('Receipts','Expenses','Net')
                self.setToolTip(f"{item['start']} — {item['end']}\n"+'\n'.join(f'{label}: {item[key]:,.0f}' for label,key in zip(labels,('income','expenses','difference'))))
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        area=self.rect().adjusted(42,18,-18,-38)
        if area.width()<1 or area.height()<1:return
        painter.setPen(QColor('#6E91A7'))
        painter.drawLine(area.left(),area.bottom(),area.right(),area.bottom())
        if not self.points:return
        highest=max(1,max(max(p['income'],p['expenses']) for p in self.points))
        step=area.width()/len(self.points)
        for index,item in enumerate(self.points):
            x=area.left()+step*(index+0.5)
            for offset,key,color in ((-9,'income','#3DD6BD'),(3,'expenses','#F3B565')):
                height=max(0,item[key])/highest*area.height()
                painter.fillRect(QRectF(x+offset,area.bottom()-height,8,height),QColor(color))
            painter.setPen(QColor('#D9E9F0'))
            label=('امسال' if index==len(self.points)-1 else f'{item["years_ago"]}-') if self.fa else ('Now' if index==len(self.points)-1 else f'-{item["years_ago"]}y')
            painter.drawText(QRectF(x-step/2,area.bottom()+5,step,24),Qt.AlignmentFlag.AlignCenter,label)

class TrendChart(QWidget):
    """Lightweight chart without optional third-party plotting dependencies."""
    def __init__(self,parent=None):
        super().__init__(parent);self.series=[];self.setMinimumHeight(190);self.setMouseTracking(True)
    def set_series(self,series):
        self.series=list(series);self.update()
    def mouseMoveEvent(self,event):
        row=nearest_point(self.series,event.position().x(),self.width(),35,18)
        if row is not None:
            self.setToolTip(f"{row['date']}\nReceipts: {row['income']:,}\nExpenses: {row['expenses']:,}")
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=self.rect().adjusted(35,18,-18,-32)
        painter.fillRect(self.rect(),QColor('#10283B'))
        painter.setPen(QColor('#92AEC1'))
        if rect.width()<=0 or rect.height()<=0:return
        painter.drawLine(rect.left(),rect.bottom(),rect.right(),rect.bottom())
        if not self.series:return
        max_y=max(1,max(max(float(p['income']),float(p['expenses'])) for p in self.series))
        for key,color in [('income','#3DD6BD'),('expenses','#F3B565')]:
            painter.setPen(QPen(QColor(color),2.5))
            points=[]
            for i,p in enumerate(self.series):
                x=rect.left()+rect.width()*i/max(1,len(self.series)-1)
                y=rect.bottom()-rect.height()*max(0,float(p[key]))/max_y
                points.append((x,y))
            for a,b in zip(points,points[1:]):painter.drawLine(int(a[0]),int(a[1]),int(b[0]),int(b[1]))
            if len(points)==1:painter.drawEllipse(int(points[0][0])-2,int(points[0][1])-2,4,4)
        painter.setPen(QColor('#D9E9F0'))
        painter.drawText(12,self.height()-9,self.series[0]['date'])
        painter.drawText(max(12,self.width()-112),self.height()-9,self.series[-1]['date'])

class OccupancyChart(QWidget):
    """Reservation-based daily occupancy chart; does not claim physical check-ins."""
    def __init__(self,parent=None):
        super().__init__(parent);self.series=[];self.setMinimumHeight(145);self.setMouseTracking(True)
    def set_series(self,series):
        self.series=list(series);self.update()
    def mouseMoveEvent(self,event):
        row=nearest_point(self.series,event.position().x(),self.width(),42,16)
        if row is not None:
            self.setToolTip(f"{row['date']}\nBooked occupancy: {row['occupancy_pct']}%")
        else:self.setToolTip('')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        area=self.rect().adjusted(42,16,-16,-27)
        if area.width()<1 or area.height()<1:return
        painter.setPen(QColor('#8CA5B8'))
        for pct in (0,50,100):
            y=area.bottom()-round(area.height()*pct/100)
            painter.drawText(5,y+4,str(pct)+'%')
            painter.drawLine(area.left(),y,area.right(),y)
        if not self.series:return
        painter.setPen(QPen(QColor('#3DD6BD'),2.5))
        points=[]
        for i,row in enumerate(self.series):
            x=area.left()+area.width()*i/max(1,len(self.series)-1)
            y=area.bottom()-area.height()*max(0,min(100,float(row['occupancy_pct'])))/100
            points.append((round(x),round(y)))
        for a,b in zip(points,points[1:]):painter.drawLine(*a,*b)
        if len(points)==1:painter.drawEllipse(points[0][0]-3,points[0][1]-3,6,6)
        painter.setPen(QColor('#D9E9F0'))
        painter.drawText(area.left(),self.height()-7,self.series[0]['date'])
        painter.drawText(max(area.left(),self.width()-105),self.height()-7,self.series[-1]['date'])

class MonthlyComparisonChart(QWidget):
    """Bilingual month-by-month receipts vs expenses visualization."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent);self.fa=fa;self.rows=[];self.raw_months=[];self.setMinimumHeight(190);self.setMouseTracking(True)
    def set_months(self,months):
        from executive_monthly_chart_v145 import chart_bars
        self.raw_months=list(months);self.rows=chart_bars(months);self.update()
    def mouseMoveEvent(self,event):
        index=nearest_category(event.position().x(),self.width(),len(self.raw_months),30,14)
        self.setToolTip(chart_tooltip(self.raw_months[index],self.fa,'monthly') if index is not None else '')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        if not self.rows:return
        left=30;right=self.width()-14;top=24;bottom=self.height()-42
        if right<=left or bottom<=top:return
        painter.setPen(QColor('#456477'))
        for fraction in (0,.5,1):
            y=int(bottom-(bottom-top)*fraction)
            painter.drawLine(left,y,right,y)
        width=(right-left)/len(self.rows)
        for i,row in enumerate(self.rows):
            x=left+i*width
            bar_width=max(2,min(24,int(width*.27)))
            for index,(key,color) in enumerate((('income','#3DD6BD'),('expenses','#F3B565'))):
                height=int((bottom-top)*row[key])
                painter.fillRect(int(x+width*.18+index*bar_width),bottom-height,bar_width,height,QColor(color))
            painter.setPen(QColor('#D9E9F0'))
            label=row['month']
            painter.drawText(int(x),bottom+18,int(width),22,Qt.AlignmentFlag.AlignCenter,label)
        painter.setPen(QColor('#3DD6BD'))
        painter.drawText(left,16,'دریافتی' if self.fa else 'Receipts')
        painter.setPen(QColor('#F3B565'))
        painter.drawText(left+95,16,'هزینه' if self.fa else 'Expenses')

class YearOverYearChart(QWidget):
    """Side-by-side current/prior cash-flow chart; handles negative net values."""
    def __init__(self,fa=False,parent=None):
        super().__init__(parent);self.fa=fa;self.values=[];self.setMinimumHeight(155);self.setMouseTracking(True)
    def set_yoy(self,yoy):
        from executive_filter_kpis_v149 import yoy_chart_values
        self.values=yoy_chart_values(yoy);self.update()
    def mouseMoveEvent(self,event):
        index=nearest_category(event.position().x(),self.width(),len(self.values),30,18)
        self.setToolTip(chart_tooltip(self.values[index],self.fa,'yoy') if index is not None else '')
        super().mouseMoveEvent(event)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),QColor('#10283B'))
        if not self.values:return
        left=30;right=self.width()-18;top=22;bottom=self.height()-35
        if right<=left or bottom<=top:return
        numbers=[float(r[k]) for r in self.values for k in ('current','previous')]
        low=min(0.0,*numbers);high=max(0.0,*numbers)
        if high==low:high=low+1
        def ypos(v):return int(top+(high-v)*(bottom-top)/(high-low))
        baseline=ypos(0)
        painter.setPen(QColor('#66859A'));painter.drawLine(left,baseline,right,baseline)
        segment=(right-left)/len(self.values)
        labels={'income':('دریافتی','Receipts'),'expenses':('هزینه','Expenses'),'difference':('اختلاف','Difference')}
        for i,record in enumerate(self.values):
            center=left+(i+.5)*segment
            bw=max(5,min(24,int(segment*.19)))
            for offset,key,color in ((-bw-2,'current','#3DD6BD'),(2,'previous','#F3B565')):
                y=ypos(record[key]);painter.fillRect(int(center+offset),min(y,baseline),bw,max(1,abs(baseline-y)),QColor(color))
            painter.setPen(QColor('#D9E9F0'))
            painter.drawText(int(left+i*segment),bottom+4,int(segment),25,Qt.AlignmentFlag.AlignCenter,labels[record['key']][0 if self.fa else 1])

class ExecutiveDashboardDialog(QDialog):
    def __init__(self,db_path,actor_id,token,language='fa',parent=None):
        super().__init__(parent)
        self.db_path=db_path;self.actor=actor_id;self.token=token;self.fa=language=='fa'
        self.worker=None;self.closing=False;self.pending=False;self.last_data=None
        self.setWindowTitle('داشبورد مدیریتی هتل' if self.fa else 'Hotel Executive Dashboard')
        self.resize(980,650)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.fa else Qt.LayoutDirection.LeftToRight)
        self.setMinimumSize(600,440)
        self.setStyleSheet("""
          QDialog { background:#0B1D2B; color:#E8F3FA; }
          QLabel { color:#E8F3FA; }
          QPushButton { background:#17445B; border:1px solid #2B6279; color:#F0FBFF;
                        border-radius:8px; padding:8px 12px; font-weight:600; }
          QPushButton:hover { background:#21627C; }
          QPushButton:disabled { background:#233643; color:#8194A2; }
          QSpinBox { background:#17364B; color:#F5FBFF; border:1px solid #3A6579;
                     border-radius:6px; padding:5px; min-width:52px; }
          QTableWidget { background:#10283B; alternate-background-color:#17364B;
                         color:#E8F3FA; gridline-color:#315064; border:0; }
          QHeaderView::section { background:#20485E; color:#F0FAFF; padding:7px; border:0; }
          QTabWidget::pane { border:1px solid #315064; border-radius:8px; }
          QTabBar::tab { background:#17364B; color:#F0FAFF; padding:9px 18px; }
          QTabBar::tab:selected { background:#28718B; }
        """)
        outer=QVBoxLayout(self)
        self.scroll=QScrollArea(self);self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self.scroll)
        self.content=QWidget();self.scroll.setWidget(self.content)
        lay=QVBoxLayout(self.content);lay.setSpacing(12);lay.setContentsMargins(16,16,16,16)
        self.kpi_grid=QGridLayout();self.kpi_grid.setSpacing(9)
        self.kpi_cards={}
        self.kpi_frames=[]
        self._kpi_columns=3
        captions={
            'occupancy_pct':('اشغال رزروی','Booked occupancy'),
            'room_count':('اتاق‌ها','Rooms'),
            'income':('دریافتی ثبت‌شده','Recorded receipts'),
            'expenses':('هزینه ثبت‌شده','Recorded expenses'),
            'cash_difference':('اختلاف جریان نقدی','Cash difference'),
            'new_reservations':('رزروهای جدید','New reservations')}
        for index,(key,(fa,en)) in enumerate(captions.items()):
            frame=QFrame();frame.setObjectName('kpiCard')
            frame.setStyleSheet('QFrame#kpiCard {background:#17364B;border:1px solid #2C5368;border-radius:12px;}')
            frame.setMinimumWidth(130)
            card_layout=QVBoxLayout(frame)
            title=QLabel(fa if self.fa else en);title.setWordWrap(True)
            title.setStyleSheet('color:#A9CBDC;font-size:12px;border:0;')
            value=QLabel('—');value.setWordWrap(True)
            value.setStyleSheet('color:#F0FAFF;font-size:20px;font-weight:700;border:0;')
            card_layout.addWidget(title);card_layout.addWidget(value)
            self.kpi_cards[key]=value
            delta=QLabel('—');delta.setWordWrap(True)
            delta.setStyleSheet('color:#B7D4E0;font-size:11px;border:0;')
            card_layout.addWidget(delta)
            self.kpi_frames.append((frame,key,delta))
            self.kpi_grid.addWidget(frame,index//3,index%3)
        lay.addLayout(self.kpi_grid)
        controls=QHBoxLayout();controls.addWidget(QLabel('بازه (روز)' if self.fa else 'Period (days)'))
        self.days=QSpinBox();self.days.setRange(1,90);self.days.setValue(30);controls.addWidget(self.days)
        self.custom_range=QPushButton('بازه دلخواه: خاموش' if self.fa else 'Custom dates: Off')
        self.custom_range.setCheckable(True)
        controls.addWidget(self.custom_range)
        self.start_date=QDateEdit();self.start_date.setCalendarPopup(True);self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date=QDateEdit();self.end_date.setCalendarPopup(True);self.end_date.setDisplayFormat('yyyy-MM-dd')
        today=date.today()
        self.start_date.setDate(today.replace(day=1));self.end_date.setDate(today)
        for control in (self.start_date,self.end_date):
            control.setVisible(False);controls.addWidget(control)
        self.jalali_start=QLineEdit();self.jalali_end=QLineEdit()
        if self.fa:
            for field,day in ((self.jalali_start,self.start_date),(self.jalali_end,self.end_date)):
                field.setPlaceholderText('۱۴۰۵/۰۷/۰۱ → 1405/07/01')
                field.setText(jalali_label(day.date().toPython()))
                field.setVisible(False);field.setMaximumWidth(135);controls.addWidget(field)
                day.setVisible(False)
        if self.fa:
            from executive_jalali_picker_v144 import JalaliDatePicker
            for field in (self.jalali_start,self.jalali_end):
                pick=QPushButton('📅')
                pick.setToolTip('انتخاب تاریخ شمسی')
                pick.clicked.connect(lambda checked=False,target=field:self.pick_jalali_date(target))
                controls.addWidget(pick)
                pick.setVisible(False)
                if not hasattr(self,'jalali_pick_buttons'):self.jalali_pick_buttons=[]
                self.jalali_pick_buttons.append(pick)
        self.custom_range.toggled.connect(self.toggle_custom_range)
        self.refresh=QPushButton('به‌روزرسانی' if self.fa else 'Refresh');controls.addWidget(self.refresh);lay.addLayout(controls)
        alert_controls=QHBoxLayout();self.threshold_inputs={}
        captions={'low_occupancy':('حد اشغال پایین','Low occupancy'), 'high_expense_ratio':('حد نسبت هزینه','Expense ratio'), 'receipts_decline':('حد افت دریافتی','Receipts drop')}
        for key,default in DEFAULTS.items():
            alert_controls.addWidget(QLabel(captions[key][0 if self.fa else 1]+' %'))
            control=QSpinBox();control.setRange(0,100);control.setValue(default)
            self.threshold_inputs[key]=control;alert_controls.addWidget(control)
        self.save_alerts=QPushButton('ذخیره هشدارها' if self.fa else 'Save alert settings')
        alert_controls.addWidget(self.save_alerts);lay.addLayout(alert_controls)
        self.save_alerts.clicked.connect(self.save_alert_settings)
        self.status=QLabel();lay.addWidget(self.status)
        self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.hide();lay.addWidget(self.progress)
        self.summary=QLabel();self.summary.setWordWrap(True);self.summary.setStyleSheet('font-size:13px;padding:12px;background:#17364B;color:#F0FAFF;border-radius:10px;');lay.addWidget(self.summary)
        self.yoy_heading=QLabel('مقایسه با بازه هم‌طول سال شمسی قبل' if self.fa else 'Same-length period one Gregorian year earlier')
        self.yoy_heading.setStyleSheet('color:#A9CBDC;font-weight:700;padding-top:8px;')
        lay.addWidget(self.yoy_heading)
        self.yoy_summary=QLabel('—');self.yoy_summary.setWordWrap(True)
        self.yoy_summary.setStyleSheet('padding:12px;background:#17364B;border-radius:10px;color:#E8F3FA;')
        lay.addWidget(self.yoy_summary)
        self.yoy_chart=YearOverYearChart(self.fa,self);lay.addWidget(self.yoy_chart)
        self.tabs=QTabWidget(self);lay.addWidget(self.tabs)
        self.trends_page=QWidget();trends_lay=QVBoxLayout(self.trends_page)
        self.chart=TrendChart(self);trends_lay.addWidget(self.chart)
        legend=QLabel('● دریافتی‌ها     ● هزینه‌ها' if self.fa else '● Receipts     ● Expenses')
        legend.setStyleSheet('color:#3DD6BD;font-weight:600;padding:5px;')
        legend.setToolTip('فیروزه‌ای: دریافتی | طلایی: هزینه' if self.fa else 'Turquoise: receipts | Gold: expenses')
        trends_lay.addWidget(legend)
        self.occupancy_title=QLabel("روند روزانه اشغال رزروی اتاق‌ها" if self.fa else "Daily reservation occupancy trend")
        trends_lay.addWidget(self.occupancy_title)
        self.occupancy_chart=OccupancyChart(self);trends_lay.addWidget(self.occupancy_chart)
        self.tabs.addTab(self.trends_page,'نمودارها' if self.fa else 'Trends')
        self.alerts_label=QLabel();self.alerts_label.setWordWrap(True)
        self.alerts_label.setStyleSheet("padding:10px;border-radius:8px;background:#294354;color:#FFF1D6;")
        lay.addWidget(self.alerts_label)
        self.room_heading=QLabel("ارزش تخمینی رزرو اتاق‌ها بر اساس نوع (نه درآمد تحقق‌یافته)" if self.fa else "Estimated booked room value by type (not recognized revenue)")
        self.room_heading.setWordWrap(True);lay.addWidget(self.room_heading)
        self.rooms_page=QWidget();rooms_lay=QVBoxLayout(self.rooms_page)
        room_filter=QHBoxLayout()
        room_filter.addWidget(QLabel('جست‌وجوی نوع اتاق' if self.fa else 'Search room types'))
        self.room_search=QLineEdit();self.room_search.setPlaceholderText('نام نوع اتاق…' if self.fa else 'Room type…')
        room_filter.addWidget(self.room_search);rooms_lay.addLayout(room_filter)
        self.room_table=QTableWidget(0,6);self.room_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.room_table.setHorizontalHeaderLabels(["نوع","اتاق","شب رزرو","ارزش رزرو","ADR تخمینی","RevPAR تخمینی"] if self.fa else ["Type","Rooms","Booked nights","Booked value","Est. ADR","Est. RevPAR"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.room_table.setSortingEnabled(True)
        self.room_search.textChanged.connect(self.filter_room_types)
        metric_line=QHBoxLayout()
        metric_line.addWidget(QLabel('شاخص مقایسه' if self.fa else 'Comparison metric'))
        self.room_metric=QComboBox()
        self.room_metric.addItem('RevPAR تخمینی' if self.fa else 'Estimated RevPAR','estimated_revpar')
        self.room_metric.addItem('ADR تخمینی' if self.fa else 'Estimated ADR','estimated_adr')
        self.room_metric.addItem('درصد اشغال رزروی' if self.fa else 'Booked occupancy %','occupancy_pct')
        self.room_metric.addItem('ارزش تخمینی رزرو' if self.fa else 'Estimated booking value','booked_value')
        metric_line.addWidget(self.room_metric)
        rooms_lay.addLayout(metric_line)
        self.room_performance_chart=RoomPerformanceChart(self.fa,self.rooms_page)
        rooms_lay.addWidget(self.room_performance_chart)
        self.room_performance_summary=QLabel();self.room_performance_summary.setWordWrap(True)
        self.room_performance_summary.setStyleSheet('padding:10px;background:#17364B;color:#E2F2F8;border-radius:8px;')
        rooms_lay.addWidget(self.room_performance_summary)
        self.room_metric.currentIndexChanged.connect(self.refresh_room_performance)
        rooms_lay.addWidget(self.room_table)
        self.tabs.addTab(self.rooms_page,'انواع اتاق' if self.fa else 'Room types')
        self.outlook_page=QWidget();outlook_layout=QVBoxLayout(self.outlook_page)
        self.outlook_note=QLabel('پوشش رزروهای ثبت‌شده؛ پیش‌بینی تقاضای واقعی نیست.' if self.fa else 'Recorded booking coverage; not a demand forecast.')
        self.outlook_note.setWordWrap(True);outlook_layout.addWidget(self.outlook_note)
        outlook_controls=QHBoxLayout()
        outlook_controls.addWidget(QLabel('بازه (روز)' if self.fa else 'Horizon (days)'))
        self.outlook_days=QSpinBox();self.outlook_days.setRange(7,90);self.outlook_days.setValue(30)
        outlook_controls.addWidget(self.outlook_days)
        outlook_controls.addWidget(QLabel('آستانه هشدار ٪' if self.fa else 'Low coverage threshold %'))
        self.outlook_threshold=QSpinBox();self.outlook_threshold.setRange(0,100);self.outlook_threshold.setValue(30)
        outlook_controls.addWidget(self.outlook_threshold)
        outlook_update=QPushButton('به‌روزرسانی' if self.fa else 'Update outlook')
        outlook_update.clicked.connect(self.load);outlook_controls.addWidget(outlook_update)
        outlook_layout.addLayout(outlook_controls)
        self.outlook_chart=BookingCoverageChart(self.fa,self)
        outlook_layout.addWidget(self.outlook_chart)
        self.outlook_summary=QLabel('—');self.outlook_summary.setWordWrap(True)
        self.outlook_summary.setStyleSheet('padding:12px;background:#17364B;color:#E8F3FA;border-radius:9px;')
        outlook_layout.addWidget(self.outlook_summary)
        self.outlook_insights=QLabel('—');self.outlook_insights.setWordWrap(True)
        self.outlook_insights.setStyleSheet('padding:10px;background:#17364B;color:#E8F3FA;border-radius:9px;')
        outlook_layout.addWidget(self.outlook_insights)
        pace_controls=QHBoxLayout()
        self.pace_min=QSpinBox();self.pace_min.setRange(0,1000);self.pace_min.setValue(1)
        self.pace_decline=QSpinBox();self.pace_decline.setRange(0,100);self.pace_decline.setValue(25)
        self.pace_cancel=QSpinBox();self.pace_cancel.setRange(0,100);self.pace_cancel.setValue(30)
        for label,control in [(('حداقل رزرو خالص روزانه' if self.fa else 'Min net/day'),self.pace_min),(('هشدار افت ٪' if self.fa else 'Decline alert %'),self.pace_decline),(('هشدار لغو ٪' if self.fa else 'Cancellation alert %'),self.pace_cancel)]:
            pace_controls.addWidget(QLabel(label));pace_controls.addWidget(control)
        outlook_layout.addLayout(pace_controls)
        self.cohort_label=QLabel('—');self.cohort_label.setWordWrap(True)
        self.cohort_label.setStyleSheet('padding:10px;background:#17364B;color:#E8F3FA;border-radius:9px;')
        outlook_layout.addWidget(self.cohort_label)
        self.cohort_chart=BookingPaceChart(self.fa,self);outlook_layout.addWidget(self.cohort_chart)
        outlook_layout.addWidget(QLabel('لغو رزرو بر اساس نوع اتاق (وضعیت فعلی)' if self.fa else 'Current cancellations by room type'))
        self.cancellation_type_table=QTableWidget(0,5)
        self.cancellation_type_table.setHorizontalHeaderLabels(['نوع اتاق','کل رزرو','لغوشده','خالص','سهم لغو ٪'] if self.fa else ['Room type','Gross','Cancelled','Net','Cancelled %'])
        self.cancellation_type_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cancellation_type_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cancellation_type_table.setMaximumHeight(210)
        outlook_layout.addWidget(self.cancellation_type_table)
        self.export_cancellation_button=QPushButton('خروجی CSV لغو رزروها' if self.fa else 'Export cancellation CSV')
        self.export_cancellation_button.clicked.connect(self.export_cancellation_types)
        outlook_layout.addWidget(self.export_cancellation_button)
        self.pace_label=QLabel('—');self.pace_label.setWordWrap(True)
        self.pace_label.setStyleSheet('padding:10px;background:#17364B;color:#E8F3FA;border-radius:9px;')
        outlook_layout.addWidget(self.pace_label)
        self.pace_table=QTableWidget(0,2)
        self.pace_table.setHorizontalHeaderLabels(['تاریخ ثبت','رزروهای جدید'] if self.fa else ['Creation date','New reservations'])
        self.pace_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pace_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pace_table.setMaximumHeight(190)
        outlook_layout.addWidget(self.pace_table)
        self.outlook_weekly=QLabel('—');self.outlook_weekly.setWordWrap(True)
        self.outlook_weekly.setStyleSheet('padding:10px;background:#17364B;color:#E8F3FA;border-radius:9px;')
        outlook_layout.addWidget(self.outlook_weekly)
        booking_exports=QHBoxLayout()
        self.outlook_export_xlsx=QPushButton('خروجی اکسل تقویم' if self.fa else 'Export booking Excel')
        self.outlook_export_pdf=QPushButton('خروجی PDF تقویم' if self.fa else 'Export booking PDF')
        self.outlook_export_xlsx.clicked.connect(lambda:self.export_booking('xlsx'))
        self.outlook_export_pdf.clicked.connect(lambda:self.export_booking('pdf'))
        booking_exports.addWidget(self.outlook_export_xlsx);booking_exports.addWidget(self.outlook_export_pdf)
        outlook_layout.addLayout(booking_exports)
        outlook_layout.addWidget(QLabel('تقویم رنگی پوشش رزرو' if self.fa else 'Booking coverage calendar'))
        self.outlook_calendar=QTableWidget(0,7)
        self.outlook_calendar.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.outlook_calendar.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.outlook_calendar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.outlook_calendar.setHorizontalHeaderLabels(['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه','جمعه'] if self.fa else ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
        self.outlook_calendar.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.outlook_calendar.verticalHeader().setVisible(False)
        self.outlook_calendar.setMinimumHeight(190)
        outlook_layout.addWidget(self.outlook_calendar)
        self.outlook_table=QTableWidget(0,4)
        self.outlook_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.outlook_table.setHorizontalHeaderLabels(['تاریخ','اتاق رزروشده','پوشش رزرو %','تقاضای پایین'] if self.fa else ['Date','Booked rooms','Booking coverage %','Low coverage'])
        self.outlook_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.outlook_table.setSortingEnabled(True)
        outlook_layout.addWidget(self.outlook_table)
        self.tabs.addTab(self.outlook_page,'چشم‌انداز رزرو' if self.fa else 'Booking outlook')

        self.daily_page=QWidget();daily_lay=QVBoxLayout(self.daily_page)
        self.table=QTableWidget(0,3);self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['تاریخ','دریافتی','هزینه'] if self.fa else ['Date','Receipts','Expenses'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.daily_search=QLineEdit()
        self.daily_search.setPlaceholderText('جست‌وجوی تاریخ (YYYY-MM-DD)…' if self.fa else 'Search date (YYYY-MM-DD)…')
        self.daily_search.textChanged.connect(self.filter_daily_rows)
        self.min_daily_amount=QSpinBox()
        self.min_daily_amount.setRange(0,2_000_000_000)
        self.min_daily_amount.setSingleStep(100_000)
        self.min_daily_amount.setPrefix('حداقل مبلغ: ' if self.fa else 'Minimum amount: ')
        self.min_daily_amount.setToolTip('نمایش روزهایی با دریافتی یا هزینه برابر یا بیشتر از مقدار انتخابی' if self.fa else 'Show days with receipts or expenses at least this amount')
        self.min_daily_amount.valueChanged.connect(self.filter_daily_rows)
        self.max_daily_amount=QSpinBox()
        self.max_daily_amount.setRange(0,2_000_000_000)
        self.max_daily_amount.setSpecialValueText('بدون سقف' if self.fa else 'No maximum')
        self.max_daily_amount.setPrefix('حداکثر: ' if self.fa else 'Maximum: ')
        self.max_daily_amount.valueChanged.connect(self.filter_daily_rows)
        self.amount_mode=QComboBox()
        self.amount_mode.addItem('دریافتی یا هزینه' if self.fa else 'Receipts or expenses','either')
        self.amount_mode.addItem('فقط دریافتی' if self.fa else 'Receipts only','receipts')
        self.amount_mode.addItem('فقط هزینه' if self.fa else 'Expenses only','expenses')
        self.amount_mode.addItem('اختلاف خالص' if self.fa else 'Net difference','net')
        self.amount_mode.currentIndexChanged.connect(self.filter_daily_rows)
        self.export_filtered=QCheckBox('خروجی فقط ردیف‌های فیلترشده' if self.fa else 'Export filtered days only')
        self.export_filtered.setToolTip('خروجی روزانه و جمع‌های ماهانه از ردیف‌های فیلترشده ساخته می‌شوند' if self.fa else 'Daily and monthly export sheets use the filtered rows')
        self.filtered_kpi_label=QLabel('—')
        self.filtered_kpi_label.setWordWrap(True)
        self.filtered_kpi_label.setStyleSheet('padding:10px;background:#17364B;border-radius:8px;color:#3DD6BD;font-weight:700;')
        daily_lay.addWidget(self.filtered_kpi_label)
        self.preset_box=QComboBox()
        self.preset_box.addItem('پروفایل فیلترها' if self.fa else 'Filter presets',None)
        self.preset_save=QPushButton('ذخیره فیلترها' if self.fa else 'Save filter preset')
        self.preset_delete=QPushButton('حذف پروفایل' if self.fa else 'Delete preset')
        self.preset_save.clicked.connect(self.save_filter_preset)
        self.preset_delete.clicked.connect(self.delete_filter_preset)
        self.preset_box.currentIndexChanged.connect(self.apply_filter_preset)
        preset_bar=QHBoxLayout();preset_bar.addWidget(self.preset_box);preset_bar.addWidget(self.preset_save);preset_bar.addWidget(self.preset_delete)
        daily_lay.addLayout(preset_bar)
        self.load_filter_presets()
        daily_lay.addWidget(self.min_daily_amount)
        daily_lay.addWidget(self.max_daily_amount)
        daily_lay.addWidget(self.amount_mode)
        daily_lay.addWidget(self.export_filtered)
        daily_lay.addWidget(self.daily_search)
        daily_lay.addWidget(self.table)
        self.tabs.addTab(self.daily_page,'عملکرد روزانه' if self.fa else 'Daily activity')
        self.monthly_page=QWidget();monthly_layout=QVBoxLayout(self.monthly_page)
        self.monthly_table=QTableWidget(0,4)
        self.monthly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.monthly_table.setHorizontalHeaderLabels(['ماه','دریافتی','هزینه','اختلاف'] if self.fa else ['Month','Receipts','Expenses','Difference'])
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.monthly_table.setSortingEnabled(True)
        self.monthly_chart=MonthlyComparisonChart(self.fa,self.monthly_page)
        monthly_layout.addWidget(self.monthly_chart)
        monthly_layout.addWidget(self.monthly_table)
        self.tabs.addTab(self.monthly_page,'گزارش ماهانه' if self.fa else 'Monthly report')
        self.history_page=QWidget(); history_layout=QVBoxLayout(self.history_page)
        history_layout.addWidget(QLabel('مقایسه جریان نقدی ثبت‌شده در دوره‌های هم‌طول' if self.fa else 'Recorded cash flow in equivalent annual windows'))
        history_bar=QHBoxLayout();history_bar.addWidget(QLabel('تعداد سال‌های گذشته' if self.fa else 'Prior years'))
        self.history_years=QComboBox()
        for count in range(1,5):self.history_years.addItem(str(count),count)
        self.history_years.setCurrentIndex(3);history_bar.addWidget(self.history_years);history_bar.addStretch()
        history_layout.addLayout(history_bar)
        self.history_chart=MultiYearTrendChart(self.fa,self.history_page)
        history_layout.addWidget(self.history_chart)
        self.history_growth=QLabel('—');self.history_growth.setWordWrap(True)
        self.history_growth.setStyleSheet('padding:10px;background:#17364B;color:#E8F3FA;border-radius:8px;')
        history_layout.addWidget(self.history_growth)
        self.history_table=QTableWidget(0,6)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setHorizontalHeaderLabels(['سال قبل','شروع','پایان','دریافتی','هزینه','اختلاف'] if self.fa else ['Years ago','Start','End','Receipts','Expenses','Difference'])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSortingEnabled(True)
        history_layout.addWidget(self.history_table)
        self.tabs.addTab(self.history_page,'مقایسه چندساله' if self.fa else 'Multi-year comparison')
        self.details=QLabel('یک روز را از جدول انتخاب کنید' if self.fa else 'Select a day in the table')
        self.details.setWordWrap(True)
        self.details.setStyleSheet('padding:12px;background:#17364B;border-radius:8px;color:#E8F3FA;')
        daily_lay.addWidget(self.details)
        self.table.itemSelectionChanged.connect(self.show_day_details)
        self.export_xlsx=QPushButton('خروجی Excel' if self.fa else 'Export Excel')
        self.export_pdf=QPushButton('خروجی PDF' if self.fa else 'Export PDF')
        self.export_xlsx.setEnabled(False);self.export_pdf.setEnabled(False)
        controls.addWidget(self.export_xlsx);controls.addWidget(self.export_pdf)
        self.export_xlsx.clicked.connect(lambda:self.export('xlsx'))
        self.export_pdf.clicked.connect(lambda:self.export('pdf'))
        self.refresh.clicked.connect(self.load);self.days.valueChanged.connect(self.load);self.history_years.currentIndexChanged.connect(self.load)
        self.load()
    def load(self,*_):
        if self.closing:return
        if self.worker is not None:
            self.pending=True;return
        self.last_data=None;self.export_xlsx.setEnabled(False);self.export_pdf.setEnabled(False)
        self.status.setText('در حال بارگذاری…' if self.fa else 'Loading…')
        self.refresh.setEnabled(False);self.progress.show()
        start=self.start_date.date().toPython() if self.custom_range.isChecked() else None
        end=self.end_date.date().toPython() if self.custom_range.isChecked() else None
        try:
            if self.fa and self.custom_range.isChecked():
                start=parse_jalali(self.jalali_start.text().strip())
                end=parse_jalali(self.jalali_end.text().strip())
            if start is not None and (end<start or (end-start).days>=90 or end>date.today()):
                raise ValueError('Invalid reporting date range')
        except ValueError:
            self.status.setText('تاریخ شمسی نامعتبر است یا بازه بیش از ۹۰ روز است' if self.fa else 'Choose a valid range of at most 90 days without future dates')
            self.refresh.setEnabled(True);self.progress.hide()
            return
        worker=ExecutiveWorker(self.db_path,self.actor,self.token,self.days.value(),self,start_date=start,end_date=end,fa=self.fa,history_years=self.history_years.currentData(),outlook_days=self.outlook_days.value(),outlook_threshold=self.outlook_threshold.value(),pace_min=self.pace_min.value(),pace_decline=self.pace_decline.value(),pace_cancel=self.pace_cancel.value())
        self.worker=worker
        worker.succeeded.connect(self.display)
        worker.failed.connect(lambda message:self.status.setText('خطا در بارگذاری داده‌ها' if self.fa else message))
        def done():
            self.worker=None;worker.deleteLater()
            if self.closing:return
            self.refresh.setEnabled(True);self.progress.hide()
            if self.pending:
                self.pending=False;self.load()
        worker.finished.connect(done)
        worker.start()
    def export_cancellation_types(self):
        data=getattr(self,'last_data',None)
        if not data or 'cancellation_by_type' not in data:
            QMessageBox.warning(self,'Export','Load dashboard data first')
            return
        path,_=QFileDialog.getSaveFileName(self,'Export cancellation report','cancellation_by_room_type.csv','CSV (*.csv)')
        if not path:return
        try:
            with open_dashboard_db(self.db_path,read_only=True) as conn:
                authorize_action(conn,self.actor,self.token,'security.view')
            export_cancellation_csv(path,data['cancellation_by_type'])
        except (OSError,sqlite3.Error,PermissionError,ValueError):
            QMessageBox.warning(self,'Export','Unable to export authorized report')

    def display(self,data):
        if self.closing or self.pending:return
        self.last_data=data;self.export_xlsx.setEnabled(True);self.export_pdf.setEnabled(True)
        for key,value in data.get('alert_settings',DEFAULTS).items():
            if key in self.threshold_inputs:self.threshold_inputs[key].setValue(value)
        c=data['current'];p=data['previous']
        for key,widget in self.kpi_cards.items():
            value=c.get(key,'—')
            widget.setText(f'{value:,}' if isinstance(value,(int,float)) else str(value))
        for frame,key,delta in self.kpi_frames:
            comparison=compare_periods(c.get(key),p.get(key))
            if comparison['kind']=='undefined':
                delta.setText('دوره قبل: صفر (بدون درصد)' if self.fa else 'Prior period: zero (no % change)')
            elif comparison['kind']=='change':
                sign='+' if comparison['percent']>0 else ''
                delta.setText(f"{sign}{comparison['percent']:.1f}% " + ('نسبت به دوره قبل' if self.fa else 'vs previous period'))
            else:
                delta.setText('بدون تغییر' if self.fa else 'No change')
            delta.setStyleSheet('color:'+('#3DD6BD' if comparison.get('percent',0)>0 else '#F3B565' if comparison.get('percent',0)<0 else '#B7D4E0')+';font-size:11px;border:0;')
        if self.fa:
            self.summary.setText(f"اتاق‌ها: {c['room_count']}  |  اشغال: {c['occupancy_pct']}٪  |  شب‌اتاق: {c['occupied_nights']} / {c['available_nights']}\nدریافتی: {c['income']:,}  |  هزینه: {c['expenses']:,}  |  خالص جریان ثبت‌شده: {c['cash_difference']:,}\nرزروهای جدید: {c['new_reservations']}  |  دوره قبل - دریافتی: {p['income']:,} / اشغال: {p['occupancy_pct']}٪")
            self.status.setText('اطلاعات به‌روز شد (مبالغ در واحد ذخیره‌شده دیتابیس)' )
        else:
            self.summary.setText(f"Rooms: {c['room_count']} | Occupancy: {c['occupancy_pct']}% | Room-nights: {c['occupied_nights']}/{c['available_nights']}\nReceipts: {c['income']:,} | Expenses: {c['expenses']:,} | Recorded cash difference: {c['cash_difference']:,}\nNew reservations: {c['new_reservations']} | Previous period receipts: {p['income']:,} / occupancy: {p['occupancy_pct']}%")
            self.status.setText('Updated (amounts use database currency units)')
        yoy=data.get('yoy',{})
        yoy_metrics=yoy.get('metrics',{})
        yoy_lines=[]
        for key,fa_label,en_label in (('income','دریافتی','Receipts'),('expenses','هزینه','Expenses'),('difference','اختلاف','Difference')):
            entry=yoy_metrics.get(key)
            if entry is None:continue
            percent=('—' if entry['percent'] is None else f"{entry['percent']:+.1f}%")
            label=fa_label if self.fa else en_label
            yoy_lines.append(f"{label}: {entry['current']:,} / {entry['previous']:,}  ({percent})")
        period=f"{yoy.get('prior_start','')} → {yoy.get('prior_end','')}"
        self.yoy_summary.setText(period+'\n'+'\n'.join(yoy_lines))
        self.yoy_chart.set_yoy(yoy)
        self.chart.set_series(data['series'])
        self.occupancy_chart.set_series(data.get('occupancy_series',[]))
        names={'low_occupancy':('اشغال پایین‌تر از حد هشدار','Occupancy below alert threshold'),
               'high_expense_ratio':('نسبت هزینه به دریافتی بالا است','Expenses are high relative to receipts'),
               'receipts_decline':('دریافتی نسبت به دوره قبل از آستانه تنظیم‌شده بیشتر کاهش یافته','Receipts fell beyond the configured threshold vs previous period')}
        messages=[names[key][0 if self.fa else 1] for key in data.get('alerts',[]) if key in names]
        self.alerts_label.setText(('هشدارهای مدیریتی: ' if self.fa else 'Management alerts: ')+(' | '.join(messages) if messages else ('موردی ثبت نشد' if self.fa else 'None')))
        self.room_table.setSortingEnabled(False)
        self.room_table.setRowCount(len(data['room_types']))
        for i,room in enumerate(data['room_types']):
            for j,key in enumerate(('type','rooms','booked_nights','booked_value','estimated_adr','estimated_revpar')):
                self.room_table.setItem(i,j,QTableWidgetItem(str(room[key])))
        self.room_table.setSortingEnabled(True)
        self.filter_room_types()
        self.refresh_room_performance()
        cohorts=data.get('booking_cohorts')
        if cohorts:
            current=cohorts['current'];prior=cohorts['previous']
            alerts=cohort_alerts(cohorts,self.pace_min.value(),self.pace_decline.value(),self.pace_cancel.value())
            delta='—' if cohorts['net_change_pct'] is None else f"{cohorts['net_change_pct']:+.1f}%"
            self.cohort_label.setText((f"رزرو ناخالص: {current['gross']} | لغوشده فعلی: {current['cancelled']} | خالص: {current['net']} | خالص دوره قبل: {prior['net']} | تغییر خالص: {delta} | سهم لغو: {current['cancelled_pct']}٪ | هشدار: {len(alerts)}" if self.fa else f"Gross: {current['gross']} | Currently cancelled: {current['cancelled']} | Net: {current['net']} | Prior net: {prior['net']} | Net change: {delta} | Cancellation share: {current['cancelled_pct']}% | Alerts: {len(alerts)}") + ('\nوضعیت لغو در زمان گزارش؛ نه تاریخ وقوع لغو.' if self.fa else '\nCurrent cancellation status, not cancellation event dates.'))
            self.cohort_chart.set_rows(cohorts['rows'])
        types=data.get('cancellation_by_type',[])
        self.cancellation_type_table.setRowCount(len(types))
        for i,record in enumerate(types):
            for j,key in enumerate(('room_type','gross','cancelled','net','cancelled_pct')):
                self.cancellation_type_table.setItem(i,j,QTableWidgetItem(str(record[key])))
        pace=data.get('booking_pace',{})
        if pace:
            change='—' if pace['change_percent'] is None else f"{pace['change_percent']:+.1f}%"
            alerts=pace_alerts(pace)
            if self.fa:
                self.pace_label.setText(f"رزروهای ثبت‌شده در بازه: {pace['current_total']} | دوره قبل: {pace['previous_total']} | تغییر: {change} | میانگین روزانه: {pace['daily_average']} | هشدار: {len(alerts)}\nشامل رزروهای بعداً لغوشده نیز می‌شود.")
            else:
                self.pace_label.setText(f"New bookings: {pace['current_total']} | Previous period: {pace['previous_total']} | Change: {change} | Daily average: {pace['daily_average']} | Alerts: {len(alerts)}\nIncludes subsequently cancelled bookings.")
            self.pace_table.setRowCount(len(pace['rows']))
            for idx,point in enumerate(pace['rows']):
                self.pace_table.setItem(idx,0,QTableWidgetItem(point['date']))
                self.pace_table.setItem(idx,1,QTableWidgetItem(str(point['new_reservations'])))
        outlook=data.get('booking_outlook',[])
        totals=outlook_summary(outlook)
        self.outlook_chart.set_rows(outlook)
        if self.fa:
            self.outlook_summary.setText(f"میانگین پوشش رزرو: {totals['average_booked_pct']}٪ | روزهای با پوشش پایین: {totals['low_demand_days']} از {totals['days']} | بیشینه: {totals['peak_booked_pct']}٪")
        else:
            self.outlook_summary.setText(f"Average booked coverage: {totals['average_booked_pct']}% | Low-coverage days: {totals['low_demand_days']} of {totals['days']} | Peak: {totals['peak_booked_pct']}%")
        insights=coverage_insights(outlook)
        if self.fa:
            self.outlook_insights.setText(f"روزهای کم‌رزرو: {insights['low']} | متوسط: {insights['medium']} | پرتراکم: {insights['high']} | طولانی‌ترین دوره کم‌رزرو: {insights['longest_low_streak']} روز (شروع: {insights['longest_low_start'] or '—'})")
        else:
            self.outlook_insights.setText(f"Low: {insights['low']} days | Moderate: {insights['medium']} | High: {insights['high']} | Longest low-coverage streak: {insights['longest_low_streak']} days (from {insights['longest_low_start'] or '—'})")
        weekly=weekly_coverage(outlook,week_start=5 if self.fa else 0)
        latest=weekly[-1] if weekly else None
        if latest:
            delta='—' if latest['change_pp'] is None else f"{latest['change_pp']:+.1f} pp"
            self.outlook_weekly.setText((f"میانگین پوشش هفته آخر: {latest['average_booked_pct']}٪ | تغییر نسبت به هفته قبل: {delta}" if self.fa else f"Latest week average coverage: {latest['average_booked_pct']}% | Change vs previous week: {delta}"))
        else:self.outlook_weekly.setText('—')
        weeks=calendar_weeks(outlook,week_start=5 if self.fa else 0)
        self.outlook_calendar.setRowCount(len(weeks))
        colors={'low':'#66431C','medium':'#164E5B','high':'#12664F','unavailable':'#35495B'}
        for week_index,week in enumerate(weeks):
            self.outlook_calendar.setRowHeight(week_index,54)
            for weekday,day in enumerate(week):
                cell=QTableWidgetItem('')
                if day is not None:
                    from datetime import date as _date
                    dt=_date.fromisoformat(day['date'])
                    label=jalali_label(dt) if self.fa else dt.strftime('%b %d')
                    cell.setText(f"{label}\n{day['booked_pct']}%")
                    cell.setBackground(QColor(colors[coverage_band(day)]))
                    cell.setForeground(QColor('#FFFFFF'))
                    cell.setToolTip(f"{day['date']} | {day['booked_rooms']}/{day['total_rooms']} rooms | {day['booked_pct']}%")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.outlook_calendar.setItem(week_index,weekday,cell)
        self.outlook_table.setSortingEnabled(False);self.outlook_table.setRowCount(len(outlook))
        for i,item in enumerate(outlook):
            values=(item['date'],item['booked_rooms'],item['booked_pct'],('بله' if self.fa else 'Yes') if item['low_demand'] else ('خیر' if self.fa else 'No'))
            for j,value in enumerate(values):
                cell=QTableWidgetItem(str(value))
                if j in (1,2):cell.setData(Qt.ItemDataRole.EditRole,value)
                self.outlook_table.setItem(i,j,cell)
        self.outlook_table.setSortingEnabled(True)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data['series']))
        for i,item in enumerate(data['series']):
            for j,key in enumerate(('date','income','expenses')):
                cell=QTableWidgetItem(str(item[key]))
                if key!='date':
                    cell.setData(Qt.ItemDataRole.EditRole,int(item[key]))
                self.table.setItem(i,j,cell)
        self.table.setSortingEnabled(True)
        self.filter_daily_rows()
        from executive_monthly_v144 import monthly_totals
        months=monthly_totals(data['series'],'jalali' if self.fa else 'gregorian')
        self.monthly_table.setSortingEnabled(False)
        self.monthly_table.setRowCount(len(months))
        for row,record in enumerate(months):
            for column,key in enumerate(('month','income','expenses','difference')):
                cell=QTableWidgetItem(str(record[key]))
                if key!='month':cell.setData(Qt.ItemDataRole.EditRole,record[key])
                self.monthly_table.setItem(row,column,cell)
        self.monthly_table.setSortingEnabled(True)
        self.monthly_chart.set_months(months)
        history=data.get('multi_year',{}).get('rows',[])
        self.history_table.setSortingEnabled(False)
        self.history_table.setRowCount(len(history))
        for row,record in enumerate(history):
            for column,key in enumerate(('years_ago','start','end','income','expenses','difference')):
                cell=QTableWidgetItem(str(record[key]))
                if key in ('years_ago','income','expenses','difference'):
                    cell.setData(Qt.ItemDataRole.EditRole,record[key])
                self.history_table.setItem(row,column,cell)
        self.history_table.setSortingEnabled(True)
        self.history_chart.set_rows(history)
        from executive_multiyear_trends_v152 import historical_trends
        points=historical_trends(history) if history else []
        if points:
            current=points[-1]
            def show_growth(key):
                value=current[key]
                return '—' if value is None else f'{value:+,.2f}%'
            self.history_growth.setText(('رشد دریافتی نسبت به سال قبل: ' if self.fa else 'Receipts YoY growth: ')+show_growth('income_growth_pct')+'  |  '+('تغییر هزینه: ' if self.fa else 'Expenses YoY change: ')+show_growth('expense_growth_pct'))
        else:self.history_growth.setText('—')

    def pick_jalali_date(self,target):
        from executive_jalali_picker_v144 import JalaliDatePicker
        try:initial=parse_jalali(target.text().strip())
        except ValueError:initial=date.today()
        dialog=JalaliDatePicker(initial,self)
        if dialog.exec() and dialog.selected:
            target.setText(jalali_label(dialog.selected))

    def toggle_custom_range(self,enabled):
        self.days.setEnabled(not enabled)
        self.start_date.setVisible(enabled and not self.fa);self.end_date.setVisible(enabled and not self.fa)
        if self.fa:
            self.jalali_start.setVisible(enabled);self.jalali_end.setVisible(enabled)
            for button in self.jalali_pick_buttons:button.setVisible(enabled)
        self.custom_range.setText(('بازه دلخواه: روشن' if enabled else 'بازه دلخواه: خاموش') if self.fa else ('Custom dates: On' if enabled else 'Custom dates: Off'))
        self.load()
    def daily_filter_options(self):
        return dict(search=self.daily_search.text(),minimum=self.min_daily_amount.value(),
                    maximum=self.max_daily_amount.value() or None,
                    mode=self.amount_mode.currentData())

    def filter_daily_rows(self,*_):
        from executive_financial_filters_v148 import filter_daily_series
        if self.last_data is None:return
        visible={row['date'] for row in filter_daily_series(self.last_data['series'],**self.daily_filter_options())}
        for row in range(self.table.rowCount()):
            item=self.table.item(row,0)
            self.table.setRowHidden(row,item is None or item.text() not in visible)
        from executive_filter_kpis_v149 import filtered_kpis
        k=filtered_kpis(self.last_data['series'],**self.daily_filter_options())
        if self.fa:
            label=f"روزهای نمایش‌داده‌شده: {k['days']} از {k['total_days']} | دریافتی: {k['income']:,} | هزینه: {k['expenses']:,} | اختلاف: {k['difference']:,}"
        else:
            label=f"Visible days: {k['days']} of {k['total_days']} | Receipts: {k['income']:,} | Expenses: {k['expenses']:,} | Net: {k['difference']:,}"
        self.filtered_kpi_label.setText(label)

    def _preset_settings(self):
        # Per-actor, per-database, per-language scope; no financial data stored.
        import hashlib
        db_key=hashlib.sha256(str(self.db_path).encode('utf-8')).hexdigest()[:20]
        return QSettings('AshkanHotelPro','ExecutiveFiltersV149'),f'{db_key}/{self.actor}/{"fa" if self.fa else "en"}'

    def load_filter_presets(self):
        settings,prefix=self._preset_settings()
        self.preset_box.blockSignals(True)
        self.preset_box.clear()
        self.preset_box.addItem('پروفایل فیلترها' if self.fa else 'Filter presets',None)
        for name in ('either','receipts','expenses','net'):
            if settings.contains(f'{prefix}/{name}'):
                self.preset_box.addItem(name,name)
        self.preset_box.blockSignals(False)

    def save_filter_preset(self):
        settings,prefix=self._preset_settings()
        name=self.amount_mode.currentData()
        import json
        settings.setValue(f'{prefix}/{name}',json.dumps(self.daily_filter_options()))
        settings.sync()
        self.load_filter_presets()
        index=self.preset_box.findData(name)
        if index>=0:self.preset_box.setCurrentIndex(index)
        self.status.setText('فیلتر ذخیره شد' if self.fa else 'Filter preset saved')

    def apply_filter_preset(self,*_):
        name=self.preset_box.currentData()
        if name is None:return
        settings,prefix=self._preset_settings()
        import json
        try:
            data=json.loads(settings.value(f'{prefix}/{name}','{}'))
            if not isinstance(data,dict) or data.get('mode') not in ('either','receipts','expenses','net'):
                raise ValueError('Invalid saved preset')
            for widget in (self.daily_search,self.min_daily_amount,self.max_daily_amount,self.amount_mode):widget.blockSignals(True)
            self.daily_search.setText(str(data.get('search','')))
            self.min_daily_amount.setValue(int(data.get('minimum',0)))
            self.max_daily_amount.setValue(int(data.get('maximum') or 0))
            self.amount_mode.setCurrentIndex(max(0,self.amount_mode.findData(data['mode'])))
        except (ValueError,TypeError,OverflowError):
            self.status.setText('پروفایل نامعتبر است' if self.fa else 'Invalid filter preset')
        finally:
            for widget in (self.daily_search,self.min_daily_amount,self.max_daily_amount,self.amount_mode):widget.blockSignals(False)
        self.filter_daily_rows()

    def delete_filter_preset(self):
        name=self.preset_box.currentData()
        if name is None:return
        settings,prefix=self._preset_settings()
        settings.remove(f'{prefix}/{name}');settings.sync()
        self.load_filter_presets()
        self.status.setText('پروفایل حذف شد' if self.fa else 'Filter preset deleted')

    def refresh_room_performance(self,*_):
        from room_performance_v153 import performance_summary
        data=getattr(self,'last_data',None)
        rows=data.get('room_types',[]) if isinstance(data,dict) else []
        metric=self.room_metric.currentData()
        self.room_performance_chart.set_rows(rows,metric)
        info=performance_summary(rows)
        if self.fa:
            message=f"انواع اتاق: {info['types']} | ارزش تخمینی رزرو: {info['total_booked_value']:,.0f} | ADR وزنی: {info['weighted_adr']:,.2f} | RevPAR وزنی: {info['weighted_revpar']:,.2f} | اشغال رزروی: {info['occupancy_pct']}٪"
        else:
            message=f"Room types: {info['types']} | Est. booked value: {info['total_booked_value']:,.0f} | Weighted ADR: {info['weighted_adr']:,.2f} | Weighted RevPAR: {info['weighted_revpar']:,.2f} | Booked occupancy: {info['occupancy_pct']}%"
        self.room_performance_summary.setText(message)

    def filter_room_types(self,*_):
        """Filter the visible room-type rows without altering authorized snapshot data."""
        query=self.room_search.text().strip().casefold()
        for row in range(self.room_table.rowCount()):
            item=self.room_table.item(row,0)
            self.room_table.setRowHidden(row,bool(query and (item is None or query not in item.text().casefold())))

    def show_day_details(self):
        """Display selected daily recorded cash flow without new database queries."""
        row=self.table.currentRow()
        if self.last_data is None or not 0<=row<len(self.last_data.get('series',[])):
            return
        from executive_daily_insights_v139 import daily_insight
        # Sorting changes the visual row order, not the underlying snapshot order.
        date_cell=self.table.item(row,0)
        selected_date=date_cell.text() if date_cell else None
        record=next((item for item in self.last_data['series'] if item['date']==selected_date),None)
        if record is None:return
        detail=daily_insight(record)
        if self.fa:
            msg=f"{detail['date']} | دریافتی: {detail['income']:,} | هزینه: {detail['expenses']:,} | اختلاف: {detail['net']:,} | نسبت هزینه: {detail['expense_ratio_label']}"
        else:
            msg=f"{detail['date']} | Receipts: {detail['income']:,} | Expenses: {detail['expenses']:,} | Difference: {detail['net']:,} | Expense ratio: {detail['expense_ratio_label']}"
        self.details.setText(msg)

    def save_alert_settings(self):
        if self.closing or self.worker is not None:return
        try:
            with open_dashboard_db(self.db_path) as conn:
                authorize_action(conn,self.actor,self.token,'security.view')
                settings={key:widget.value() for key,widget in self.threshold_inputs.items()}
                with conn:save_alert_settings(conn,self.actor,settings)
            self.status.setText('آستانه‌ها ذخیره شدند' if self.fa else 'Alert thresholds saved')
            self.load()
        except (sqlite3.Error,PermissionError,ValueError):
            QMessageBox.warning(self,'Alerts','ذخیره تنظیمات ناموفق بود' if self.fa else 'Could not save alert settings')

    def export_booking(self,fmt):
        if self.closing or self.worker is not None or self.last_data is None:return
        ext='xlsx' if fmt=='xlsx' else 'pdf'
        path,_=QFileDialog.getSaveFileName(self,'Booking coverage',f'booking_coverage.{ext}',f'{ext.upper()} Files (*.{ext})')
        if not path:return
        if not path.lower().endswith('.'+ext):path+='.'+ext
        try:
            with open_dashboard_db(self.db_path,read_only=True) as conn:
                authorize_action(conn,self.actor,self.token,'security.view')
            rows=self.last_data.get('booking_outlook',[])
            (export_booking_excel if fmt=='xlsx' else export_booking_pdf)(rows,path,fa=self.fa)
            self.status.setText('گزارش رزرو ذخیره شد' if self.fa else 'Booking report saved')
        except (OSError,ValueError,ImportError,sqlite3.Error,PermissionError) as exc:
            QMessageBox.warning(self,'Booking export',str(exc))

    def export(self,fmt):
        if self.closing or self.worker is not None or self.last_data is None:return
        from executive_dashboard_export_v133 import export_excel,export_pdf
        ext='xlsx' if fmt=='xlsx' else 'pdf'
        path,_=QFileDialog.getSaveFileName(self,'Export',f'executive_dashboard.{ext}',f'{ext.upper()} Files (*.{ext})')
        if not path:return
        if not path.lower().endswith('.'+ext):path+='.'+ext
        try:
            # Re-authorize at export time: permissions/sessions may have changed
            # since the snapshot was originally loaded.
            with open_dashboard_db(self.db_path,read_only=True) as conn:
                authorize_action(conn,self.actor,self.token,'security.view')
            from executive_financial_filters_v148 import filtered_snapshot
            report=filtered_snapshot(self.last_data,**self.daily_filter_options()) if self.export_filtered.isChecked() else dict(self.last_data)
            report['monthly_calendar']='jalali' if self.fa else 'gregorian'
            (export_excel if fmt=='xlsx' else export_pdf)(report,path)
            self.status.setText('خروجی ذخیره شد' if self.fa else 'Export saved')
        except (OSError,ValueError,ImportError,sqlite3.Error,PermissionError) as exc:
            QMessageBox.warning(self,'Export',str(exc))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'monthly_chart'):
            self.monthly_chart.setMinimumHeight(responsive_chart_height(self.width(),220,170,300))
        if hasattr(self,'yoy_chart'):
            self.yoy_chart.setMinimumHeight(responsive_chart_height(self.width(),175,145,250))
        if hasattr(self,'chart'):
            self.chart.setMinimumHeight(responsive_chart_height(self.width(),190,155,260))
        if hasattr(self,'kpi_frames') and hasattr(self,'kpi_grid'):
            columns=responsive_columns(self.width())
            if columns!=self._kpi_columns:
                self._kpi_columns=columns
                for index,(frame,_,_) in enumerate(self.kpi_frames):
                    self.kpi_grid.removeWidget(frame)
                    self.kpi_grid.addWidget(frame,index//columns,index%columns)

    def closeEvent(self,event):
        self.closing=True
        if self.worker is not None and self.worker.isRunning():
            self.worker.requestInterruption()
            if not self.worker.wait(5000):
                self.closing=False;event.ignore();return
        event.accept()
