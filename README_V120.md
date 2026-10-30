# Ashkan Hotel Pro Enterprise — Stage 120

## System health analytics and reporting

- Administrator-only `system_health_reports_v120.py` reads up to 500 historical health checks without creating new observations.
- Health indicator (`healthy`, `warning`, `no_data`), warning rate, last healthy observation, daily check/warning counts, maximum recorded failure count.
- Excel workbook with Summary, History, Daily trends, and a bar chart (openpyxl).
- PDF health report with daily trends and summary (ReportLab); bilingual FA/EN titles.
- System Health dialog adds indicator summary and Excel/PDF export actions.
- Permission is checked in the GUI and service layer. Excel strings are escaped against formula injection.
- Exporting does not run a new database health check. Click **Run health check** to create a fresh observation.

## Run

```powershell
py -m pip install -r requirements.txt
py main.py
```

In the admin console open **User and role management → System health**.

## Testing

```bash
python -m unittest discover -s tests -q
```

### Notes

The indicator summarizes recorded observations, not continuous uptime or a comprehensive database audit. The newest 100 checks are included in exports by default. The PDF requires an installed Unicode-capable font for proper Persian text. GUI rendering and Windows packaging have not been tested here. Back up `hotel.db` before upgrading.
