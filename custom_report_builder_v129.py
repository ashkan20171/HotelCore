# Read-only permission-gated health report builder
import re
from datetime import datetime, timezone, timedelta
from user_access_management import _actor
from system_health_v119 import migrate as migrate_health
from system_health_reports_v120 import _safe_cell

FIELDS = ('checked_at', 'database_status', 'monitor_state', 'failure_count')
HEADERS = {'fa': ('زمان UTC', 'وضعیت دیتابیس', 'وضعیت پایش', 'تعداد خطاها'),
           'en': ('UTC time', 'Database status', 'Monitor state', 'Failure count')}
_NAME = re.compile(r'^[\w -]{1,40}$', re.UNICODE)

def validate(columns, days, status='all', limit=250):
    if not isinstance(columns, (tuple, list)) or not columns or len(set(columns)) != len(columns) or any(c not in FIELDS for c in columns):
        raise ValueError('Choose unique, supported report columns')
    if type(days) is not int or not 1 <= days <= 365: raise ValueError('Days must be 1..365')
    if status not in ('all', 'ok', 'warning'): raise ValueError('Unsupported status filter')
    if type(limit) is not int or not 1 <= limit <= 1000: raise ValueError('Limit must be 1..1000')

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS health_custom_templates (
        actor_id INTEGER NOT NULL, name TEXT NOT NULL,
        columns_csv TEXT NOT NULL, days INTEGER NOT NULL, status TEXT NOT NULL,
        PRIMARY KEY(actor_id, name))''')

def save_template(conn, actor_id, name, columns, days, status='all'):
    _actor(conn, actor_id)
    validate(columns, days, status)
    if not isinstance(name, str) or not _NAME.fullmatch(name) or name != name.strip():
        raise ValueError('Invalid template name')
    migrate(conn)
    existing = conn.execute('SELECT COUNT(*) FROM health_custom_templates WHERE actor_id=?',(actor_id,)).fetchone()[0]
    found = conn.execute('SELECT 1 FROM health_custom_templates WHERE actor_id=? AND name=?',(actor_id,name)).fetchone()
    if existing >= 20 and not found: raise ValueError('Maximum 20 templates per administrator')
    conn.execute('''INSERT INTO health_custom_templates(actor_id,name,columns_csv,days,status) VALUES(?,?,?,?,?)
        ON CONFLICT(actor_id,name) DO UPDATE SET columns_csv=excluded.columns_csv, days=excluded.days,status=excluded.status''',
        (actor_id,name,','.join(columns),days,status))
    conn.commit()

def list_templates(conn, actor_id):
    _actor(conn, actor_id)
    migrate(conn)
    return [(name, tuple(csv.split(',')), days, status) for name,csv,days,status in conn.execute(
        'SELECT name,columns_csv,days,status FROM health_custom_templates WHERE actor_id=? ORDER BY name',(actor_id,)).fetchall()]

def delete_template(conn, actor_id, name):
    _actor(conn, actor_id)
    if not isinstance(name,str) or not _NAME.fullmatch(name): raise ValueError('Invalid template name')
    migrate(conn)
    cursor=conn.execute('DELETE FROM health_custom_templates WHERE actor_id=? AND name=?',(actor_id,name))
    conn.commit()
    return cursor.rowcount > 0

def fetch_report(conn, actor_id, *, columns=FIELDS, days=30, status='all', limit=250, now=None):
    _actor(conn, actor_id)
    validate(columns,days,status,limit)
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None: raise ValueError('now must be timezone aware')
    migrate_health(conn)
    cutoff=(now.astimezone(timezone.utc)-timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S')
    end=now.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    # Identifiers are chosen exclusively from the fixed FIELDS allowlist.
    sql='SELECT '+','.join(columns)+' FROM system_health_checks WHERE checked_at>=? AND checked_at<=?'
    if status=='ok': sql+=' AND database_status=?'; params=[cutoff,end,'ok']
    elif status=='warning': sql+=' AND database_status<>?'; params=[cutoff,end,'ok']
    else: params=[cutoff,end]
    sql+=' ORDER BY id DESC LIMIT ?';params.append(limit)
    return conn.execute(sql,params).fetchall()

def write_excel(path, columns, rows, language='en'):
    if language not in HEADERS: raise ValueError('Unsupported language')
    validate(columns,30)
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    wb=Workbook(); ws=wb.active;ws.title='Health Report'
    ws.append([HEADERS[language][FIELDS.index(c)] for c in columns])
    for row in rows: ws.append([_safe_cell(v) for v in row])
    ws.freeze_panes='A2';ws.sheet_view.rightToLeft=(language=='fa')
    for cell in ws[1]:
        cell.fill=PatternFill('solid',fgColor='15344B');cell.font=Font(bold=True,color='FFFFFF')
    for index in range(1,len(columns)+1):
        from openpyxl.utils import get_column_letter
        ws.column_dimensions[get_column_letter(index)].width=27
    wb.save(str(path));return len(rows)

def write_pdf(path, columns, rows, language='en'):
    if language not in HEADERS: raise ValueError('Unsupported language')
    validate(columns,30)
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4,landscape
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    font='Helvetica'
    if language=='fa':
        for candidate in ('C:/Windows/Fonts/tahoma.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
            if os.path.exists(candidate):
                font='HealthReportUnicode';pdfmetrics.registerFont(TTFont(font,candidate));break
        else: raise RuntimeError('A Unicode font is required for Persian PDF reports')
        import arabic_reshaper
        from bidi.algorithm import get_display
        def shape(value):return get_display(arabic_reshaper.reshape(str(value)))
    else:
        def shape(value):return str(value)
    styles=getSampleStyleSheet()
    doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),leftMargin=28,rightMargin=28)
    table_rows=[[shape(HEADERS[language][FIELDS.index(c)]) for c in columns]]
    table_rows.extend([[shape(v if v is not None else '—') for v in row] for row in rows])
    table=Table(table_rows,repeatRows=1,hAlign='CENTER',colWidths=[(landscape(A4)[0]-56)/len(columns)]*len(columns))
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#15344B')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,-1),font),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#E9F3F5')]),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),
        ('FONTSIZE',(0,0),(-1,-1),8)]))
    doc.build([table]);return len(rows)
