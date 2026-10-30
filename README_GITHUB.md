# Ashkan Hotel Pro Enterprise

**Bilingual desktop hotel management platform | Python · PySide6 · SQLite**

An extensible hotel operations and property management portfolio project, designed around practical workflows, readable architecture, secure role-based access and Persian/English localization. Built to demonstrate desktop application engineering for international software teams.

> **Portfolio project, not a certified production PMS.** Test with synthetic data before deployment. Review privacy, security, backups and jurisdiction-specific requirements before using guest data in production.

## Highlights

- **Hotel operations:** reservations, room and guest workflows, operational dashboards and reporting modules.
- **Bilingual UX:** Persian right-to-left and English left-to-right interface.
- **Access control:** administrator-restricted operational/security analytics and authorization checks for protected actions.
- **System health:** historical checks, daily charts, period-over-period comparisons and KPI indicators.
- **Background processing:** cancellable Qt workers for health analytics and report generation.
- **PDF & Excel exports:** atomic file publishing to reduce the risk of partial output files.
- **Report Center (v127):** administrator-only export audit trail with filename search, status/format filters, UTC timestamps, record counts and outcomes. Stores **filenames only**, not full paths or tokens.
- **Maintainability:** modular Python services, SQLite persistence, automated unit tests and versioned release notes.

## Technology stack

| Layer | Technology |
| --- | --- |
| Language | Python 3 |
| Desktop UI | PySide6 / Qt Widgets |
| Persistence | SQLite |
| Reports | ReportLab, openpyxl |
| Localization | Persian RTL, English LTR; jdatetime |
| Testing | Python unittest |

## Quick start (Windows 11)

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

To run automated tests:

```powershell
python -m unittest discover -s tests -q
```

Back up `hotel.db` before upgrading. Do not commit guest records, real credentials, generated reports or local database files to GitHub.

## Report Center — v127

Navigate to the administrator's **System Health** screen. The Report Center shows PDF/XLSX export attempts, including successful, failed and cancelled outcomes. Filter by format or status and search by filename. The audit table does not store document contents, full local paths or authentication tokens. A saved report can be generated again using the export controls; automatic replay of historical exports is **not** implemented.

## Quality & limitations

- Automated test suite: **736 tests discovered; 720 passed, 16 skipped** in the supplied test environment.
- Desktop behavior, layouts, printer/export integrations and Qt worker lifecycle require real Windows GUI verification.
- SQLite suits a single-instance/local application; multi-user network deployments need additional architecture and concurrency review.
- No claim of GDPR certification, payment compliance, penetration testing or production readiness.

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md), [`SECURITY.md`](SECURITY.md), and [`README_V127.md`](README_V127.md).

## Recruiter snapshot

**English:** Desktop application engineering, modular Python architecture, role-based access, background workers, SQLite, bilingual UX and automated testing.

**Deutsch:** Zweisprachige Hotelmanagement-Desktopanwendung mit Python, PySide6 und SQLite. Schwerpunkte: saubere Softwarearchitektur, rollenbasierte Zugriffskontrolle, asynchrone Verarbeitung, Reporting und automatisierte Tests.

**فارسی:** سامانه مدیریت هتل با پشتیبانی کامل از فارسی و انگلیسی، گزارش‌گیری، کنترل دسترسی، پردازش غیرهم‌زمان و ساختار ماژولار قابل توسعه.
