"""
Are American workers actually better off than before the pandemic?

Question: Nominal pay has risen a lot since 2020, but so have prices.
Did the typical production / nonsupervisory worker gain purchasing power?

Data (FRED, Federal Reserve Bank of St. Louis, retrieved Nov 2026):
  - AHETPI: Average Hourly Earnings of Production and Nonsupervisory
    Employees, Total Private, dollars per hour, seasonally adjusted.
  - CPIAUCSL: Consumer Price Index for All Urban Consumers: All Items,
    index 1982-84 = 100, seasonally adjusted.
  - Monthly, Jan 2019 - Sep 2026 (latest available at time of analysis).

Method:
  - Real hourly earnings = AHETPI / CPIAUCSL * 100.
  - Everything indexed to Jan 2020 = 100 so nominal pay, prices, and
    real pay are comparable on one chart.
  - Oct 2025 CPI has no observation on FRED, so it is linearly
    interpolated between Sep and Nov 2025 (flagged in the output).
  - Headline numbers are also computed with SQL (SQLite) to show the
    same results can be produced with a query, not just pandas.

Note on Apr 2020: the spike in average earnings that month is mostly a
composition effect (lower-wage workers were laid off first, which lifted
the average), not a raise for the typical worker. The analysis focuses
on Jan 2020 vs. the latest month and on the post-spike trough instead.
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# ---- Load and clean -------------------------------------------------------
ahe = pd.read_csv(DATA / "AHETPI.csv", parse_dates=["DATE"])
cpi = pd.read_csv(DATA / "CPIAUCSL.csv", parse_dates=["DATE"])
ahe.columns = ["date", "nominal_pay"]
cpi.columns = ["date", "cpi"]

df = ahe.merge(cpi, on="date", how="inner").sort_values("date")
df["cpi"] = pd.to_numeric(df["cpi"], errors="coerce")  # "." = missing on FRED
missing_cpi = df[df["cpi"].isna()]["date"].dt.strftime("%Y-%m").tolist()
df["cpi"] = df["cpi"].interpolate(limit_direction="both")

# ---- Real pay and indexes (Jan 2020 = 100) --------------------------------
df["real_pay"] = df["nominal_pay"] / df["cpi"] * 100
base = df.loc[df["date"] == "2020-01-01"].iloc[0]
df["nominal_index"] = df["nominal_pay"] / base["nominal_pay"] * 100
df["cpi_index"] = df["cpi"] / base["cpi"] * 100
df["real_index"] = df["real_pay"] / base["real_pay"] * 100

# ---- Headline numbers via SQL ---------------------------------------------
conn = sqlite3.connect(":memory:")
df.to_sql("monthly", conn, index=False)
q = lambda sql: conn.execute(sql).fetchone()
first = q("SELECT date, nominal_pay, cpi, real_index FROM monthly "
          "WHERE date LIKE '2020-01-01%'")
last = q("SELECT date, nominal_pay, cpi, real_index FROM monthly "
         "ORDER BY date DESC LIMIT 1")
trough = q("SELECT date, real_index FROM monthly "
           "WHERE date >= '2020-05-01' ORDER BY real_index ASC LIMIT 1")
peak = q("SELECT date, real_index FROM monthly "
         "WHERE date >= '2020-05-01' ORDER BY real_index DESC LIMIT 1")

print(f"Base month:      {first[0][:7]}  pay ${first[1]:.2f}/hr, CPI {first[2]:.1f}")
print(f"Latest month:    {last[0][:7]}  pay ${last[1]:.2f}/hr, CPI {last[2]:.1f}")
print(f"Nominal pay change Jan 2020 -> latest: "
      f"{(last[1] / first[1] - 1) * 100:+.1f}%")
print(f"Price change (CPI) Jan 2020 -> latest: "
      f"{(last[2] / first[2] - 1) * 100:+.1f}%")
print(f"Real pay change Jan 2020 -> latest:    "
      f"{(last[3] / 100 - 1) * 100:+.1f}% (index {last[3]:.1f})")
print(f"Post-spike trough: {trough[0][:7]} (real index {trough[1]:.1f})")
print(f"Post-spike peak:   {peak[0][:7]} (real index {peak[1]:.1f})")
if missing_cpi:
    print(f"Note: CPI missing for {', '.join(missing_cpi)} on FRED; "
          f"linearly interpolated.")

# ---- Chart -----------------------------------------------------------------
plt.figure(figsize=(10, 5.5))
plt.plot(df["date"], df["nominal_index"], label="Nominal hourly pay", linewidth=2)
plt.plot(df["date"], df["cpi_index"], label="Prices (CPI)", linewidth=2)
plt.plot(df["date"], df["real_index"], label="Real hourly pay", linewidth=2.5)
plt.axhline(100, color="grey", linewidth=0.8, linestyle="--")
plt.axvline(pd.Timestamp("2020-04-01"), color="grey",
            linewidth=0.8, linestyle=":")
plt.text(pd.Timestamp("2020-04-01"), 132, " Apr 2020 spike\n (composition effect)",
         fontsize=8, color="grey")
plt.title("Are workers better off than before the pandemic?\n"
          "Hourly pay vs. prices, Jan 2020 = 100")
plt.ylabel("Index (Jan 2020 = 100)")
plt.legend()
plt.tight_layout()
plt.savefig(HERE / "real_pay_vs_prices.png", dpi=150)
print("Chart saved to real_pay_vs_prices.png")
