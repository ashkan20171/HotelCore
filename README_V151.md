# Stage 151 — Multi-year recorded cash flow

- Authorized read-only worker queries recorded receipts and expenses for the selected reporting period and the same-length period in each of four previous calendar years.
- Persian mode anchors comparisons on Jalali year boundaries; English mode uses Gregorian years. All SQL date ranges are inclusive at day level with exclusive upper timestamps.
- New bilingual **Multi-year comparison** dashboard tab includes a sortable 5-row table.
- Excel and PDF exports include a separate multi-year comparison section when snapshot data includes it.
- Reports reflect recorded cash movements, not recognized accounting revenue or forecasts.
- A maximum of five windows (current + four prior) and 90 days per window limits workload.
- Existing daily filters do not affect historical period totals; this is intentional and displayed as independent historical data.
- Qt GUI appearance and Windows packaging still require manual testing on Windows.
