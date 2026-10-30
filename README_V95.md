# Ashkan Hotel Pro v95

## Improvements
- Persistent occupancy and missing-quote alert thresholds via per-user, per-branch Qt QSettings.
- Administrator-only CSV comparison of indicative room-type KPIs across authorized active branches.
- Branch access verified for every branch; no guest names or payment records in the comparison.
- Excel-compatible UTF-8 CSV with formula-injection protection.
- Dedicated `executive_room_report.py` for authorization, threshold validation and export.

## Important limitations
Accommodation values are **indicative quote allocations, not recognized revenue**. Current room inventory is not a historical snapshot. Local QSettings are device-local, not server-synchronized.

## Run
```powershell
py -m pip install -r requirements.txt
py main.py
```
Back up `hotel.db` before upgrading. Test the UI on your Windows system.
