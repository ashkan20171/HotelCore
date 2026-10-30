"""Printable bilingual executive PDF, containing authorized aggregated branch data only."""
from datetime import date
from html import escape
from pathlib import Path

LABELS={
 'en':('Multi-property executive report','Period','Property','Rooms','Occupancy %','Indicative ADR','Indicative RevPAR','Missing quotes','Alerts','None','Indicative reservation quotes, NOT recognized revenue. Inventory reflects current room assignments.'),
 'fa':('گزارش مدیریتی شعب هتل','دوره','شعبه','اتاق‌ها','درصد اشغال','ADR تخمینی','RevPAR تخمینی','نرخ‌های ناقص','هشدارها','ندارد','ارزش‌ها برآوردی هستند و درآمد قطعی حسابداری محسوب نمی‌شوند. ظرفیت بر اساس موجودی فعلی است.')}
ALERTS={'missing_quotes':('Missing quotes','رزرو بدون نرخ'),'overcapacity':('Overcapacity','بیش از ظرفیت'),'no_active_rooms':('No active rooms','بدون اتاق فعال'),'low_occupancy':('Low occupancy','اشغال پایین')}

def export_property_pdf(path, rows, *, start, end, title=None, language='en'):
    """Write an English or properly shaped Persian PDF; raise for missing RTL dependencies."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    from reportlab.lib.units import mm
    date.fromisoformat(start);date.fromisoformat(end)
    if end<=start:raise ValueError('Invalid report window')
    if language not in LABELS:raise ValueError('Unsupported language')
    rtl=language=='fa'
    if rtl:
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError as exc:
            raise ImportError('Persian PDF requires arabic-reshaper and python-bidi') from exc
        fonts=['/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
               'C:/Windows/Fonts/tahoma.ttf']
        font=next((f for f in fonts if Path(f).is_file()),None)
        if not font:raise RuntimeError('Persian PDF needs a Unicode TTF font (Noto Sans Arabic or Tahoma)')
        pdfmetrics.registerFont(TTFont('HotelPersian',font))
        font_name='HotelPersian'
        def display(value):return get_display(arabic_reshaper.reshape(str(value)))
    else:
        font_name='Helvetica'
        def display(value):return str(value)
    labels=LABELS[language]
    styles=getSampleStyleSheet()
    normal=ParagraphStyle('hotelNormal',parent=styles['Normal'],fontName=font_name,fontSize=9,leading=15,alignment=2 if rtl else 0)
    heading=ParagraphStyle('hotelHeading',parent=normal,fontSize=17,leading=26,textColor=colors.HexColor('#0F766E'))
    def paragraph(value,style=normal):return Paragraph(escape(display(value)),style)
    def value(v):return '—' if v is None else f'{v:,.2f}' if isinstance(v,float) else str(v)
    doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),leftMargin=14*mm,rightMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm)
    story=[paragraph(title or labels[0],heading),paragraph(f'{labels[1]}: {start} – {end}'),Spacer(1,6*mm)]
    data=[[paragraph(x) for x in labels[2:9]]]
    for row in rows:
        alerts=', '.join(ALERTS.get(code,(code,code))[1 if rtl else 0] for code in row.get('alerts',[])) or labels[9]
        data.append([paragraph(row.get('branch_name','')),paragraph(value(row.get('rooms'))),paragraph(value(row.get('occupancy_percent'))),paragraph(value(row.get('estimated_adr'))),paragraph(value(row.get('estimated_revpar'))),paragraph(value(row.get('missing_quotes'))),paragraph(alerts)])
    widths=[49,19,29,36,41,28,65]
    if rtl:
        data=[list(reversed(row)) for row in data]
        widths=list(reversed(widths))
    table=LongTable(data,colWidths=[w*mm for w in widths],repeatRows=1,hAlign='CENTER')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0F766E')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F1F5F9')]),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8)]))
    story.extend([table,Spacer(1,7*mm),paragraph(labels[10])])
    doc.build(story)
    return len(rows)
