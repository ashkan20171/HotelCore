"""Bilingual room-transfer PDF export with embedded Unicode fonts and RTL shaping."""
from pathlib import Path
from xml.sax.saxutils import escape
from room_transfer_analytics import summarize_transfers


def find_unicode_font(font_path=None):
    """Locate an installed Persian-capable TTF; never bundle third-party fonts."""
    candidates = [font_path] if font_path else []
    candidates += [
        'C:/Windows/Fonts/tahoma.ttf', 'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def shape_pdf_text(value, language='fa'):
    """Escape XML and reshape Persian text for ReportLab (which lacks RTL shaping)."""
    raw = str(value if value is not None else '')
    if language != 'fa':
        return escape(raw)
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError as exc:
        raise ImportError('Persian PDF requires arabic-reshaper and python-bidi') from exc
    return escape(get_display(arabic_reshaper.reshape(raw)))


def export_transfers_pdf(path, rows, *, language='fa', font_path=None):
    """Export authorized, filtered records; input must be branch-scoped by caller."""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    fa = language == 'fa'
    font = 'Helvetica'
    font_file = find_unicode_font(font_path)
    if fa and not font_file:
        raise RuntimeError('No Persian-capable TTF found. Install Tahoma or Noto Sans Arabic.')
    if font_file:
        font = 'AshkanHotelUnicode'
        if font not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font, font_file))
    data = list(rows)
    stats = summarize_transfers(data)
    base = getSampleStyleSheet()
    body = ParagraphStyle('TransferBody', parent=base['Normal'], fontName=font,
                          fontSize=8, leading=14, alignment=TA_RIGHT if fa else TA_LEFT)
    title_style = ParagraphStyle('TransferTitle', parent=body, fontSize=16, leading=24,
                                 textColor=colors.HexColor('#17324D'), spaceAfter=12)
    def paragraph(value, style=body):
        return Paragraph(shape_pdf_text(value, language), style)
    title = 'اشکان هتل پرو | گزارش انتقال اتاق‌ها' if fa else 'Ashkan Hotel Pro | Room Transfer Audit'
    count = f'تعداد کل انتقال‌ها: {stats["total"]}' if fa else f'Total transfers: {stats["total"]}'
    headers = ['شناسه', 'زمان', 'رزرو', 'اتاق مبدأ', 'اتاق مقصد', 'کاربر'] if fa else [
        'ID', 'Timestamp', 'Reservation', 'From room', 'To room', 'Actor']
    story = [paragraph(title, title_style), paragraph(count), Spacer(1, 14)]
    # Reverse columns for natural RTL reading while preserving the data schema.
    matrix = [headers] + [list(record) for record in data]
    if not data:
        matrix.append(['—', 'بدون انتقال' if fa else 'No transfers', '—', '—', '—', '—'])
    if fa:
        matrix = [list(reversed(row)) for row in matrix]
    cells = [[paragraph(value) for value in row] for row in matrix]
    table = LongTable(cells, colWidths=[130, 80, 80, 75, 125, 50] if fa else [50, 125, 75, 80, 80, 130], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#17324D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#EEF5F8')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    # Header needs its own white font; Paragraph controls foreground.
    head = ParagraphStyle('TransferHeader', parent=body, textColor=colors.white)
    cells[0][:] = [paragraph(v, head) for v in matrix[0]]
    story.append(table)
    SimpleDocTemplate(str(path), pagesize=landscape(A4), leftMargin=28,
                      rightMargin=28, topMargin=34, bottomMargin=34,
                      title=title, author='Ashkan Hotel Pro').build(story)
    return stats
