# Ashkan Hotel Pro v62 — Management Alerts

Adds configurable cashflow alerts to the Branch Analytics dashboard.

- User-scoped threshold persisted in QSettings; default 0.
- Two informational rules: current negative net exceeding threshold; period-on-period net deterioration exceeding threshold.
- Both periods are fetched with existing `cashflow` branch authorization and filtered branch selection.
- Persian and English alert table, summary and severity highlighting.
- `branch_alerts.py` contains dependency-free rules with 13 unit tests.

The financial measures are cash movement, not accrual profit. Thresholds are integer currency units. The Windows GUI has not been integration-tested in this environment. Back up `hotel.db` before upgrading.
