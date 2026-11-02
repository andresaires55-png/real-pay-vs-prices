# Are American workers actually better off than before the pandemic?

Nominal pay is up a lot since 2020 — but so are prices. This project checks
whether the typical production / nonsupervisory worker actually gained
purchasing power, using data from FRED (Federal Reserve Bank of St. Louis).

## The answer

**Yes, but only barely: real hourly pay is up 5.1% since January 2020.**

| | Jan 2020 | Sep 2026 (latest) | Change |
|---|---|---|---|
| Nominal hourly pay | $23.91 | $32.60 | **+36.3%** |
| Prices (CPI) | 259.1 | 336.3 | **+29.8%** |
| Real hourly pay | — | — | **+5.1%** |

The path matters too: real pay bottomed in **June 2022** (index 101.1) when
inflation peaked, then recovered steadily through 2023–2025. It peaked in
**February 2026** (index 106.0) and has flattened since.

## Data

- `AHETPI` — Average Hourly Earnings of Production and Nonsupervisory
  Employees, Total Private, dollars per hour, seasonally adjusted.
- `CPIAUCSL` — Consumer Price Index for All Urban Consumers: All Items,
  index 1982–84 = 100, seasonally adjusted.
- Monthly, January 2019 – September 2026, in `data/`.

## Method

1. Real hourly pay = nominal pay / CPI × 100.
2. Nominal pay, prices, and real pay are each indexed to Jan 2020 = 100 so
   they can be compared on one chart.
3. Headline numbers are computed twice: once in pandas and once with SQL
   queries (SQLite) — see `analysis.py`.
4. FRED has no CPI observation for October 2025, so that month is linearly
   interpolated between September and November 2025.

## Caveats

- The April 2020 spike in average earnings is mostly a composition effect:
  lower-wage workers were laid off first, which lifted the average. It is
  not a raise for the typical worker, which is why the analysis compares
  Jan 2020 to the latest month rather than to the spike.
- AHETPI covers production and nonsupervisory employees only, not all
  workers (managers and executives excluded).

## How to run

```bash
pip install pandas matplotlib
python analysis.py
```

Outputs `real_pay_vs_prices.png` and prints the headline numbers.

## Skills used

Python (pandas, matplotlib), SQL (SQLite), FRED data, data cleaning
(missing-value interpolation), index construction, charting.
