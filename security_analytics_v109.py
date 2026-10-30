# Bounded security event analytics
from datetime import datetime, timedelta, timezone
from user_access_management import _actor

OUTCOMES=('success','failure','locked')

def security_activity(conn, actor_id, *, days=7, now=None, username=None, limit=100):
    _actor(conn, actor_id)
    if type(days) is not int or not 1 <= days <= 90:
        raise ValueError('days must be 1..90')
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError('limit must be 1..500')
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError('now must be timezone-aware')
    end=now.astimezone(timezone.utc).isoformat()
    start=(now.astimezone(timezone.utc)-timedelta(days=days)).isoformat()
    params=[start,end]
    clause='WHERE e.occurred_at>=? AND e.occurred_at<=?'
    if username:
        clause+=' AND u.username=?'
        params.append(username)
    records=conn.execute("""SELECT e.occurred_at, COALESCE(u.username,'—'), e.outcome
       FROM login_events e LEFT JOIN users u ON u.id=e.user_id """+clause+
       ' ORDER BY e.id DESC LIMIT ?',(*params,limit)).fetchall()
    totals=dict.fromkeys(OUTCOMES,0)
    for outcome,count in conn.execute("""SELECT e.outcome, COUNT(*) FROM login_events e
       LEFT JOIN users u ON u.id=e.user_id """+clause+' GROUP BY e.outcome',params):
        if outcome in totals:totals[outcome]=count
    # A repeated failure count is a review signal, not proof of intrusion.
    suspicious=conn.execute("""SELECT u.username,COUNT(*) AS attempts FROM login_events e
       JOIN users u ON u.id=e.user_id """+clause+""" AND e.outcome IN ('failure','locked')
       GROUP BY u.id HAVING COUNT(*)>=5 ORDER BY attempts DESC LIMIT 20""",params).fetchall()
    return {'totals':totals,'records':records,'review_candidates':suspicious,'days':days}
