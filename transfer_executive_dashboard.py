"""Presentation-ready transfer KPIs. Pure, read-only transformation."""

def dashboard(rows, *, search='', order='transfers', descending=True):
    valid = {'transfers', 'reservations', 'source_rooms', 'destination_rooms', 'active_staff'}
    if order not in valid:
        raise ValueError('Unsupported sort metric')
    text = search.strip().casefold()
    filtered = [dict(r) for r in rows if text in str(r['branch']).casefold()]
    filtered.sort(key=lambda r: ((-int(r[order]) if descending else int(r[order])), str(r['branch']).casefold(), int(r['branch_id'])))
    totals = {'branches':len(filtered), 'transfers':sum(int(r['transfers']) for r in filtered),
              'reservations':sum(int(r['reservations']) for r in filtered),
              'active_staff_by_branch':sum(int(r['active_staff']) for r in filtered)}
    maximum = max((int(r[order]) for r in filtered), default=0)
    ranked = [{**r, 'rank':i+1, 'bar_percent':round(100*int(r[order])/maximum) if maximum else 0}
              for i,r in enumerate(filtered)]
    return {'rows':ranked,'totals':totals,'metric':order}
