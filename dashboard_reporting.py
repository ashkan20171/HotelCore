"""Date-window reporting helpers for a branch-scoped management dashboard."""
from datetime import date, timedelta


def reporting_window(end_date, days=30):
    """Return inclusive ISO date bounds for the last N calendar days."""
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)
    if not isinstance(end_date, date) or isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 366:
        raise ValueError("A valid end date and a 1–366 day period are required")
    return (end_date - timedelta(days=days-1)).isoformat(), end_date.isoformat()


def payment_totals(connection, branch_id, start, end):
    """Aggregate payments for one branch only; end date is inclusive."""
    if not isinstance(branch_id, int) or isinstance(branch_id, bool) or branch_id <= 0:
        raise ValueError("A valid branch ID is required")
    if date.fromisoformat(start) > date.fromisoformat(end):
        raise ValueError("Start must not follow end")
    row = connection.execute("""SELECT COUNT(*),COALESCE(SUM(p.amount),0)
        FROM payments p JOIN reservations r ON r.id=p.reservation_id
        WHERE r.branch_id=? AND date(p.created_at)>=? AND date(p.created_at)<=?""",
        (branch_id,start,end)).fetchone()
    return {'payments': int(row[0]), 'revenue': int(row[1])}


def compare_periods(current, previous):
    """Percentage change or None when baseline is zero."""
    if current < 0 or previous < 0:
        raise ValueError('Totals must be nonnegative')
    return None if previous == 0 else round((current-previous)*100/previous,1)
