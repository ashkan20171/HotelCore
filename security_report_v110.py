"""Admin-gated login security report: daily trends and bilingual PDF export."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from security_analytics_v109 import security_activity


def daily_login_trends(conn, actor_id, *, days=7, now=None, username=None):
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('days must be 1..90')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    now = now.astimezone(timezone.utc)
    # Reuse the existing administrator gate before reading the full event history.
    security_activity(conn, actor_id, days=days, now=now, username=username, limit=1)
    start = (now - timedelta(days=days-1)).date()
    end = now.date()
    params = [start.isoformat(), (end + timedelta(days=1)).isoformat()]
    clause = "WHERE e.occurred_at >= ? AND e.occurred_at < ?"
    if username:
        clause += ' AND u.username=?'
        params.append(username)
    query = ("SELECT substr(e.occurred_at,1,10), e.outcome, count(*) "
             "FROM login_events e LEFT JOIN users u ON u.id=e.user_id " + clause +
             " GROUP BY substr(e.occurred_at,1,10),e.outcome")
    counts = defaultdict(int)
    for day, outcome, count in conn.execute(query, params):
        if outcome in ('success', 'failure', 'locked'):
            counts[(day, outcome)] += count
    return [( (start + timedelta(days=i)).isoformat(),
              counts[((start + timedelta(days=i)).isoformat(),'success')],
              counts[((start + timedelta(days=i)).isoformat(),'failure')],
              counts[((start + timedelta(days=i)).isoformat(),'locked')])
            for i in range(days)]


def write_security_pdf(path, conn, actor_id, *, days=7, now=None, username=None, language='fa'):
    if language not in ('fa','en'):
        raise ValueError('Unsupported language')
    activity = security_activity(conn, actor_id, days=days, now=now, username=username, limit=100)
    trends = daily_login_trends(conn, actor_id, days=days, now=now, username=username)
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from pathlib import Path
    font = 'Helvetica'
    for candidate in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                      'C:/Windows/Fonts/tahoma.ttf', 'C:/Windows/Fonts/arial.ttf'):
        if Path(candidate).exists():
            try:
                pdfmetrics.registerFont(TTFont('HotelUnicode', candidate))
                font = 'HotelUnicode'
                break
            except Exception:
                pass
    def localize(text):
        if language != 'fa':
            return str(text)
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(str(text)))
        except ImportError:
            return str(text)
    style = ParagraphStyle('report', parent=getSampleStyleSheet()['Normal'], fontName=font,
                           fontSize=10, leading=16, alignment=TA_RIGHT if language=='fa' else TA_LEFT)
    heading = ParagraphStyle('heading', parent=style, fontSize=16, leading=23, spaceAfter=12)
    doc = SimpleDocTemplate(str(path), pagesize=(595,842), leftMargin=36,rightMargin=36)
    title = 'گزارش امنیت ورود کاربران' if language=='fa' else 'Login Security Report'
    story=[Paragraph(localize(title),heading)]
    story.append(Paragraph(localize(('بازه: ' if language=='fa' else 'Period: ')+str(days)+(' روز' if language=='fa' else ' days')),style))
    story.append(Paragraph(localize(('کاربر: ' if language=='fa' else 'User: ')+(username or ('همه' if language=='fa' else 'All'))),style))
    story.append(Spacer(1,16))
    totals=activity['totals']
    story.append(Paragraph(f"Success: {totals['success']}   Failure: {totals['failure']}   Locked: {totals['locked']}",style))
    story.append(Spacer(1,14))
    rows=[['Date','Success','Failure','Locked']]+[[str(v) for v in row] for row in trends]
    table=Table(rows,repeatRows=1,colWidths=[170,115,115,115])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#16354b')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,-1),font),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white]),
        ('GRID',(0,0),(-1,-1),.25,colors.HexColor('#b5c5d2')),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]))
    story.append(table)
    story.append(Spacer(1,14))
    label='حساب‌های نیازمند بررسی: ' if language=='fa' else 'Accounts for review: '
    candidates=', '.join(f'{name} ({count})' for name,count in activity['review_candidates']) or '—'
    story.append(Paragraph(localize(label+candidates),style))
    story.append(Spacer(1,8))
    disclaimer='این موارد صرفاً نشانه‌های نیازمند بررسی هستند.' if language=='fa' else 'Review signals are not proof of an attack.'
    story.append(Paragraph(localize(disclaimer),style))
    doc.build(story)
    return len(trends)
