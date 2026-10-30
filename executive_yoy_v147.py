"""Year-over-year comparisons on the user's selected calendar.

The calendar shifts the beginning of an inclusive window by one year;
comparison windows always contain the same number of Gregorian days.
"""
from datetime import date, timedelta
from executive_yoy_v146 import previous_year_window, cash_totals, compare


def previous_jalali_year_window(start, end):
    if not isinstance(start,date) or not isinstance(end,date) or start>end:
        raise ValueError('Invalid date window')
    days=(end-start).days
    if days>=90:raise ValueError('At most 90 days')
    import jdatetime
    jalali=jdatetime.date.fromgregorian(date=start)
    try:
        previous=jdatetime.date(jalali.year-1,jalali.month,jalali.day)
    except ValueError:
        # Esfand 30 does not exist in every Jalali year.
        previous=jdatetime.date(jalali.year-1,jalali.month,29)
    prior_start=previous.togregorian()
    return prior_start,prior_start+timedelta(days=days)


def year_over_year_calendar(conn,start,end,current,calendar='gregorian'):
    if calendar not in ('gregorian','jalali'):
        raise ValueError('Unsupported calendar')
    prior_start,prior_end=(previous_jalali_year_window(start,end) if calendar=='jalali'
                           else previous_year_window(start,end))
    prior=cash_totals(conn,prior_start,prior_end)
    return {'prior_start':prior_start.isoformat(), 'prior_end':prior_end.isoformat(),
            'calendar':calendar,'metrics':compare(current,prior)}
