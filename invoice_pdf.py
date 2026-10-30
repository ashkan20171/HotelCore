"""Bilingual PDF invoice layout and text shaping (no Qt dependency)."""
from pathlib import Path

LABELS = {
 'fa': ('صورتحساب اقامت | Ashkan Hotel Pro','شماره رزرو','نام مهمان','شماره اتاق','ورود','خروج','تعداد شب','هزینه اقامت','خدمات','تخفیف','مالیات','مبلغ کل','دریافتی','مانده','این صورتحساب سند رسمی مالیاتی نیست.'),
 'en': ('Accommodation Invoice | Ashkan Hotel Pro','Reservation ID','Guest','Room','Check-in','Check-out','Nights','Accommodation','Services','Discount','Tax','Total','Paid','Balance','This is not an official tax invoice.')
}

def invoice_lines(invoice, language, date_formatter, money_formatter):
    if language not in LABELS: raise ValueError('Unsupported language')
    l=LABELS[language]
    required=('id','guest','room','start','end','nights','accommodation','services','discount','tax','total','paid','balance')
    missing=[k for k in required if k not in invoice]
    if missing: raise ValueError('Missing invoice fields: '+', '.join(missing))
    return [l[0], f'{l[1]}: {invoice["id"]}',f'{l[2]}: {invoice["guest"]}',f'{l[3]}: {invoice["room"]}',
            f'{l[4]}: {date_formatter(invoice["start"])}',f'{l[5]}: {date_formatter(invoice["end"])}',
            f'{l[6]}: {invoice["nights"]}',f'{l[7]}: {money_formatter(invoice["accommodation"])}',
            f'{l[8]}: {money_formatter(invoice["services"])}',f'{l[9]}: {money_formatter(invoice["discount"])}',
            f'{l[10]}: {money_formatter(invoice["tax"])}',f'{l[11]}: {money_formatter(invoice["total"])}',
            f'{l[12]}: {money_formatter(invoice["paid"])}',f'{l[13]}: {money_formatter(invoice["balance"])}',l[14]]

def choose_font(language, candidates=None):
    if language not in LABELS: raise ValueError('Unsupported language')
    if candidates is None:
        candidates=[Path('C:/Windows/Fonts/tahoma.ttf'),Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    return next((Path(p) for p in candidates if Path(p).is_file()),None)

def write_invoice_pdf(path, invoice, language='fa', date_formatter=str, money_formatter=str, font_path=None):
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    lines=invoice_lines(invoice,language,date_formatter,money_formatter)
    font_path=Path(font_path) if font_path else choose_font(language)
    if font_path is None or not font_path.is_file():
        raise FileNotFoundError('A TrueType font supporting Persian/English is required')
    font_name='AshkanHotelInvoice'
    pdfmetrics.registerFont(TTFont(font_name,str(font_path)))
    pdf=canvas.Canvas(str(path),pagesize=(595,842))
    pdf.setTitle(f'Hotel invoice {invoice["id"]}')
    pdf.setFillColorRGB(.04,.09,.17);pdf.rect(0,0,595,842,fill=1,stroke=0)
    pdf.setFillColorRGB(.08,.75,.68);pdf.rect(0,812,595,30,fill=1,stroke=0)
    pdf.setFillColorRGB(.92,.97,1)
    try:
        if language=='fa':
            from arabic_reshaper import reshape
            from bidi.algorithm import get_display
            transform=lambda line:get_display(reshape(line))
        else:transform=lambda line:line
        for idx,line in enumerate(lines):
            pdf.setFont(font_name, 14 if idx==0 else 11)
            y=775-idx*43
            if language=='fa':pdf.drawRightString(555,y,transform(str(line)))
            else:pdf.drawString(40,y,str(line))
        pdf.save()
    except Exception:
        # ReportLab output is only finalized after save; caller reports the failure.
        raise
