"""Permission-gated, read-only operational reporting with allowlisted SQL projections."""
from datetime import datetime, timedelta, timezone
from user_access_management import _actor

REPORTS = {
    'reservations': {
        'source': 'reservations r JOIN rooms rm ON rm.id=r.room_id JOIN guests g ON g.id=r.guest_id',
        'date': 'r.created_at',
        'columns': {'reservation_id':'r.id', 'room':'rm.number', 'guest':'g.name', 'checkin':'r.checkin', 'checkout':'r.checkout', 'status':'r.status', 'created_at':'r.created_at'},
        'default': ('reservation_id','room','guest','checkin','checkout','status')},
    'rooms': {
        'source': 'rooms rm', 'date': None,
        'columns': {'room':'rm.number','type':'rm.kind','rate':'rm.rate','status':'rm.status'},
        'default': ('room','type','rate','status')},
    'guests': {
        'source': 'guests g', 'date': None,
        'columns': {'guest_id':'g.id','name':'g.name'},
        'default': ('guest_id','name')},
    'payments': {
        'source': 'payments p JOIN reservations r ON r.id=p.reservation_id JOIN rooms rm ON rm.id=r.room_id',
        'date': 'p.created_at',
        'columns': {'payment_id':'p.id','reservation_id':'p.reservation_id','room':'rm.number','amount':'p.amount','method':'p.method','created_at':'p.created_at'},
        'default': ('payment_id','reservation_id','room','amount','method','created_at')},
    'expenses': {
        'source': 'expenses e', 'date': 'e.created_at',
        'columns': {'expense_id':'e.id','category':'e.category','description':'e.description','amount':'e.amount','created_at':'e.created_at'},
        'default': ('expense_id','category','description','amount','created_at')},
}

HEADERS = {'fa': {'reservation_id':'شناسه رزرو','room':'اتاق','guest':'مهمان','checkin':'ورود','checkout':'خروج','status':'وضعیت','created_at':'زمان ثبت','type':'نوع اتاق','rate':'نرخ','guest_id':'شناسه مهمان','name':'نام','payment_id':'شناسه پرداخت','amount':'مبلغ','method':'روش','expense_id':'شناسه هزینه','category':'دسته‌بندی','description':'شرح'},
           'en': {'reservation_id':'Reservation ID','room':'Room','guest':'Guest','checkin':'Check-in','checkout':'Check-out','status':'Status','created_at':'Created at','type':'Room type','rate':'Rate','guest_id':'Guest ID','name':'Name','payment_id':'Payment ID','amount':'Amount','method':'Method','expense_id':'Expense ID','category':'Category','description':'Description'}}

def validate(report, columns, days=30, limit=250):
    if report not in REPORTS: raise ValueError('Unsupported report')
    allowed=REPORTS[report]['columns']
    if not isinstance(columns,(tuple,list)) or not columns or len(columns)>len(allowed) or len(set(columns))!=len(columns) or any(c not in allowed for c in columns):
        raise ValueError('Invalid report columns')
    if type(days) is not int or not 1<=days<=365: raise ValueError('Days must be 1..365')
    if type(limit) is not int or not 1<=limit<=1000: raise ValueError('Limit must be 1..1000')

def fetch(conn, actor_id, *, report, columns, days=30, limit=250, now=None):
    _actor(conn,actor_id)
    validate(report,columns,days,limit)
    now=now or datetime.now(timezone.utc)
    if not isinstance(now,datetime) or now.tzinfo is None: raise ValueError('Aware UTC datetime required')
    spec=REPORTS[report]
    sql='SELECT '+','.join(spec['columns'][c] for c in columns)+' FROM '+spec['source']
    params=[]
    if spec['date']:
        # SQLite CURRENT_TIMESTAMP dates are stored as 'YYYY-MM-DD HH:MM:SS'.
        cutoff=(now.astimezone(timezone.utc)-timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        end=now.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        sql+=' WHERE '+spec['date']+' >= ? AND '+spec['date']+' <= ?'
        params.extend((cutoff,end))
    sql+=' ORDER BY '+(spec['date'] or list(spec['columns'].values())[0])+' DESC LIMIT ?'
    params.append(limit)
    return conn.execute(sql,params).fetchall()

def write_excel(path,columns,rows,language='en'):
    if language not in HEADERS: raise ValueError('Unsupported language')
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    from system_health_reports_v120 import _safe_cell
    wb=Workbook();ws=wb.active;ws.title='Hotel Report'
    ws.sheet_view.rightToLeft=(language=='fa')
    ws.append([HEADERS[language][c] for c in columns])
    for row in rows:ws.append([_safe_cell(value) for value in row])
    ws.freeze_panes='A2'
    for cell in ws[1]:cell.fill=PatternFill('solid',fgColor='15344B');cell.font=Font(bold=True,color='FFFFFF')
    for i in range(len(columns)):ws.column_dimensions[get_column_letter(i+1)].width=26
    wb.save(str(path));return len(rows)

def write_pdf(path,columns,rows,language='en'):
    if language not in HEADERS: raise ValueError('Unsupported language')
    # Reuse tested PDF generation, passing a safe per-column translated header map.
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape,A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font='Helvetica'
    if language=='fa':
        from pathlib import Path
        for path_candidate in ('C:/Windows/Fonts/tahoma.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
            if Path(path_candidate).is_file():
                font='HotelUnicode';pdfmetrics.registerFont(TTFont(font,path_candidate));break
        else:raise RuntimeError('Unicode font is required for Persian PDF')
        import arabic_reshaper
        from bidi.algorithm import get_display
        def shape(s):return get_display(arabic_reshaper.reshape(str(s)))
    else:
        def shape(s):return str(s)
    cells=[[shape(HEADERS[language][c]) for c in columns]]
    cells.extend([[shape('—' if value is None else value) for value in row] for row in rows])
    doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),leftMargin=25,rightMargin=25)
    table=Table(cells,repeatRows=1,colWidths=[(landscape(A4)[0]-50)/len(columns)]*len(columns))
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#15344B')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,-1),font),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#E9F3F5')]),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    doc.build([table]);return len(rows)
