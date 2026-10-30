"""Permission-scoped branch cash-movement PDF renderer.

Caller MUST supply already authorized, filtered and sorted rows. No database access here.
"""
from datetime import date, timedelta
from pathlib import Path
from branch_aggregates import visible_totals

HEADERS = {'fa': ('شعبه', 'دریافتی', 'هزینه', 'خالص گردش وجوه'),
           'en': ('Branch', 'Receipts', 'Expenses', 'Net cash movement')}


def validate_report(rows, start, end, language='fa'):
    if language not in HEADERS:
        raise ValueError('Unsupported language')
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first >= last:
        raise ValueError('Invalid reporting interval')
    checked = []
    for row in rows:
        if not isinstance(row.get('branch'), str):
            raise ValueError('Invalid branch name')
        clean = {'branch': row['branch']}
        for key in ('receipts', 'expenses', 'net'):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('Financial amounts must be integers')
            clean[key] = value
        checked.append(clean)
    return checked, visible_totals(checked), first, last - timedelta(days=1)


def write_branch_comparison_pdf(path, *, rows, start, end, language='fa', font_path=None):
    """Create a bilingual, paginated comparison PDF. End date is exclusive."""
    clean, totals, first, last = validate_report(rows, start, end, language)
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from invoice_pdf import choose_font
    font = Path(font_path) if font_path else choose_font(language)
    if font is None or not font.is_file():
        raise FileNotFoundError('Unicode TrueType font required')
    font_name = 'AshkanBranchComparisonPDF'
    pdfmetrics.registerFont(TTFont(font_name, str(font)))
    if language == 'fa':
        from arabic_reshaper import reshape
        from bidi.algorithm import get_display
        shape = lambda x: get_display(reshape(str(x)))
    else:
        shape = str
    align = TA_RIGHT if language == 'fa' else TA_LEFT
    title_style = ParagraphStyle('comparison-title', fontName=font_name, fontSize=16, leading=25,
                                 textColor=colors.HexColor('#17324C'), alignment=align, spaceAfter=10)
    cell_style = ParagraphStyle('comparison-cell', fontName=font_name, fontSize=8, leading=13,
                                alignment=align)
    def paragraph(value, style=cell_style):
        import html
        return Paragraph(html.escape(shape(value)), style)
    def fmt(number):
        return f'{number:,}'
    labels = HEADERS[language]
    data = [list(labels)]
    data += [[row['branch'], fmt(row['receipts']), fmt(row['expenses']), fmt(row['net'])] for row in clean]
    data.append([('جمع کل' if language == 'fa' else 'TOTAL'), fmt(totals['receipts']),
                 fmt(totals['expenses']), fmt(totals['net'])])
    if language == 'fa':
        data = [list(reversed(row)) for row in data]
    table = Table([[paragraph(v) for v in row] for row in data], colWidths=[125, 110, 110, 160], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#087E8B')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DDEBF1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F0F5F8')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    heading = 'مقایسه گردش وجوه شعب' if language == 'fa' else 'Branch Cash Movement Comparison'
    interval = f'{first.isoformat()} — {last.isoformat()}'
    note = ('این گزارش گردش وجوه است، نه صورت سود و زیان تعهدی.' if language == 'fa'
            else 'This is a cash movement report, not an accrual profit-and-loss statement.')
    doc = SimpleDocTemplate(str(path), pagesize=(595, 842), leftMargin=42, rightMargin=42,
                            topMargin=44, bottomMargin=44, title='Ashkan Hotel Pro | Branch Comparison')
    doc.build([paragraph(heading, title_style), paragraph(interval),
               paragraph(f"{totals['branches']} " + ('شعبه' if language == 'fa' else 'branches')),
               Spacer(1, 16), table, Spacer(1, 18), paragraph(note)])
    return Path(path)
