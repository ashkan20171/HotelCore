# Enterprise release checklist

- [ ] Back up production database with `enterprise_cli.py backup`
- [ ] Confirm `enterprise_cli.py health` succeeds
- [ ] Run `py -m unittest discover -s tests -q`
- [ ] Test Persian RTL and English LTR on Windows 11
- [ ] Verify login, permissions, reservations, invoices, cashflow, dashboards and exports
- [ ] Confirm no real guest information or database is included in ZIP/Git
- [ ] Review and rotate bootstrap credentials
- [ ] Test PDF Persian fonts and Excel exports on a target machine
- [ ] Verify restore from a copied backup in an isolated environment
