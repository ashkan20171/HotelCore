"""Safe bilingual invoice HTML; monetary amounts remain denominated in toman."""
import html

LABELS = {
    'شماره رزرو':'Reservation ID','مهمان':'Guest','اتاق':'Room',
    'ورود':'Check-in','خروج':'Check-out','شب اقامت':'Nights',
    'اقامت':'Accommodation','خدمات':'Services','جمع اولیه':'Subtotal',
    'تخفیف':'Discount','مالیات':'Tax','مبلغ نهایی':'Grand total',
    'دریافتی':'Paid','مانده':'Balance',
}

def render_invoice(fields, language='fa'):
    """Render trusted labels and HTML-escaped values, preserving stored data."""
    if language not in ('fa','en'):
        raise ValueError('Unsupported language')
    direction='rtl' if language=='fa' else 'ltr'
    title='صورتحساب هتل' if language=='fa' else 'Hotel invoice'
    disclaimer=('پیش‌فاکتور محاسباتی؛ سند رسمی مالیاتی نیست.' if language=='fa'
                else 'Pro forma estimate; not an official tax invoice.')
    body=''.join('<p><b>'+html.escape(LABELS.get(str(key),str(key)) if language=='en' else str(key),quote=True)+'</b>: '+html.escape(str(value),quote=True)+'</p>' for key,value in fields)
    return f'<div dir="{direction}" style="font-family:Tahoma,Arial"><h2>{html.escape(title)}</h2>{body}<small>{html.escape(disclaimer)}</small></div>'
