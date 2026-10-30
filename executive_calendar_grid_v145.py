"""Pure Jalali calendar month-grid calculations, Saturday-first."""
from datetime import date

def month_grid(year,month):
    import jdatetime
    if type(year) is not int or type(month) is not int or not 1200<=year<=1600 or not 1<=month<=12:
        raise ValueError('Invalid Jalali month')
    first=jdatetime.date(year,month,1).togregorian()
    offset=(first.weekday()+2)%7  # Python Monday=0; Saturday=0
    if month<7:count=31
    elif month<12:count=30
    else:
        try:jdatetime.date(year,12,30);count=30
        except ValueError:count=29
    cells=[None]*offset+[day for day in range(1,count+1)]
    cells.extend([None]*((-len(cells))%7))
    return [cells[i:i+7] for i in range(0,len(cells),7)]

def adjacent_month(year,month,offset):
    if type(year) is not int or type(month) is not int or type(offset) is not int or not 1<=month<=12:
        raise ValueError('Invalid month')
    index=year*12+month-1+offset
    result=divmod(index,12)
    if not 1200<=result[0]<=1600:raise ValueError('Outside supported years')
    return result[0],result[1]+1
