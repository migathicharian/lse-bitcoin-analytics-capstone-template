# BRK metrics parquet student guide

This note describes **`brk_metrics.parquet`**, a long-format daily table of Bitcoin analytics metrics. It is written for students who are new to BRK- or StackSats-style data.

**How to use this file:** put `brk_metrics.parquet` in your working directory and run the Python examples from that directory (or pass an explicit path to `scan_parquet`).

## Resources

- [StackSats documentation](https://hypertrial.github.io/stacksats/)
- [StackSats on GitHub](https://github.com/hypertrial/stacksats)
- [StackSats BRK data source overview](https://hypertrial.github.io/stacksats/data-source/)
- [StackSats merged metrics data guide](https://hypertrial.github.io/stacksats/reference/merged-metrics-data-guide/)
- [StackSats merged metrics taxonomy](https://hypertrial.github.io/stacksats/reference/merged-metrics-taxonomy/)
- [BRK project](https://github.com/bitcoinresearchkit/brk)

## Start here

`brk_metrics.parquet` holds many thousands of **daily** time series keyed by name in the `metric` column. Example questions you can explore:

- How did market capitalization change over time?
- How do valuation ratios such as `mvrv` behave across cycles?
- How do short-term vs. long-term holder metrics compare?
- How do mining, fees, supply, UTXO, or address-balance metrics evolve?

The metrics come from the broader **BRK** ecosystem. **StackSats** documents the same long-format shape and naming conventions; treat its docs as a **glossary** when a `metric` string is hard to read.

## Vocabulary

| Term | Meaning |
|------|---------|
| BRK | Bitcoin Research Kit, the upstream analytics ecosystem behind many Bitcoin metrics. |
| StackSats | Python library and docs for Bitcoin strategy research on BRK-style data. |
| Parquet | Columnar file format; efficient for large analytic tables. |
| Metric | One named series (e.g. `market_cap`, `mvrv`). |
| Long format | Names live in a `metric` column and values live in `value`, instead of one column per series. |
| Runtime projection | Optional wide parquet (`date`, `price_usd`, features) for StackSats runtime code. |

## What this file is

- A **daily** fact table: each row is one numeric observation for one `metric` on one UTC calendar day (`day_utc`).
- **Not** a wide table: you filter or pivot by `metric` when you want columns per series.
- **Not** raw blockchain data: there are no per-transaction, per-block, or intraday rows.
- **Not** a price-only table: it includes valuation, holders, mining, supply, UTXO, and other domains.

## Physical schema

| Column | Polars dtype | Nulls (profiled) | Meaning |
|--------|--------------|------------------|---------|
| `day_utc` | `Date` | 0 | UTC calendar day. |
| `metric` | `String` | 0 | Metric key (namespace-style name). |
| `value` | `Float64` | 0 | Numeric value for that day and metric. |

Think of it as a spreadsheet with only three columns: date, metric name, and value. The `metric` key often encodes cohorts, units, windows, or transforms, such as `_ema` or `_30d_change`.

## Dataset profile

Measured with **Polars** on a local `brk_metrics.parquet` (same layout as described in StackSats’ merged-metrics schema page).

| Property | Value |
|----------|------:|
| File size | `1,160,686,731` bytes (~`1.08` GiB) |
| Rows | `236,259,020` |
| Distinct days | `6,274` |
| Distinct metrics | `41,407` |
| Top-level families (StackSats taxonomy docs) | `284` |
| Day range | `2009-01-03` to `2026-03-13` |
| Nulls (`day_utc`, `metric`, `value`) | `0` each |
| All `value` finite | yes (local check) |

If your file differs, re-run the profile query in the examples section.

## Metric domains

Category and family counts are from StackSats’ merged-metrics documentation and match this file’s scale (`41,407` metrics). Treat this table as a map of the metric namespace.

| Category | Metrics | Families | What it covers |
|----------|--------:|---------:|----------------|
| Address balance cohorts | `5,249` | `1` | Addresses by balance bucket. |
| Benchmarks, path metrics, technical indicators | `392` | `21` | DCA/lump-sum ladders, rolling paths, indicators. |
| Blocks, transactions, network activity | `295` | `47` | Throughput, activity, utilization. |
| Holder cohorts | `842` | `2` | Short-term vs long-term holders. |
| Market and valuation | `6,475` | `28` | Price, caps, realized value, ratios. |
| Mining pools and miner economics | `4,936` | `162` | Pool share, fees, hash economics. |
| Profitability and SOPR | `74` | `15` | Profit/loss and SOPR-style metrics. |
| Script and output types | `2,042` | `12` | `p2*`, unknown, empty, `OP_RETURN`, etc. |
| Supply, issuance, scarcity | `29` | `8` | Supply, subsidy, inflation. |
| UTXO age cohorts | `18,339` | `1` | UTXOs by age bucket. |
| Vintage and halving cohorts | `2,734` | `2` | By year or halving epoch. |

**Easy starting domains for coursework:** market and valuation, profitability and SOPR, supply and scarcity.

## Naming patterns

Names are **namespace-oriented**. Examples:

- `adjusted_sopr_7d_ema`: adjusted SOPR with a 7-day exponential moving average.
- `addrs_above_100btc_under_1k_btc__30d_change_usd`: address cohort, 30-day change in USD.

| Domain | Example patterns |
|--------|------------------|
| Market and valuation | `price_*`, `market_*`, `realized_*`, `mvrv`, `investor_*`, `cost_*` |
| Profitability and SOPR | `*_sopr*`, `*_profit*`, `*_loss*`, `capitulation_*`, `pain_*` |
| Supply and scarcity | `supply_*`, `circulating_*`, `subsidy_*`, `inflation_*` |
| Holder cohorts | `sth_*`, `lth_*` |
| UTXO age cohorts | `utxos_<age_bucket>_*` |
| Address balance cohorts | `addrs_<balance_bucket>_*` |
| Vintage / halving | `year_<yyyy>_*`, `epoch_<n>_*` |
| Mining | `<pool>_blocks_mined`, `<pool>_dominance`, `hash_price_*`, `fee_*` |
| Script / output types | `p2*_*`, `unknown_*`, `empty_*`, `opreturn_*`, `segwit_*`, `taproot_*` |
| Network activity | `block_*`, `tx_*`, `hash_rate`, `difficulty*`, `sent*`, `received*` |
| Benchmarks / paths | `1m_*`, `1y_*`, `10y_*`, `dca_*`, `rsi_*`, `macd_*` |

**Largest families:** `utxos` (`18,339`), `price` (`6,050`), `addrs` (`5,249`), `year` (`2,135`), `epoch` (`599`), `sth` / `lth`, and many `p2*` script families.

Common suffix dimensions include units (`usd`, `btc`, `sats`), transforms (`ema`, `ratio`, `growth_rate`), windows (`7d`, `30d`, `1y`), and cohort labels.

## Example Polars queries

Uses [Polars](https://pola.rs/). Install: `pip install polars`.

**Profile the file**

```python
import polars as pl
from pathlib import Path

p = Path("brk_metrics.parquet")
lf = pl.scan_parquet(p)

print(lf.collect_schema())
print(
    lf.select(
        pl.len().alias("rows"),
        pl.col("day_utc").n_unique().alias("unique_days"),
        pl.col("metric").n_unique().alias("unique_metrics"),
        pl.col("day_utc").min().alias("min_day"),
        pl.col("day_utc").max().alias("max_day"),
        pl.col("day_utc").null_count().alias("null_day_utc"),
        pl.col("metric").null_count().alias("null_metric"),
        pl.col("value").null_count().alias("null_value"),
    ).collect()
)
```

**One metric as a time series**

```python
import polars as pl

mvrv = (
    pl.scan_parquet("brk_metrics.parquet")
    .filter(pl.col("metric") == "mvrv")
    .select("day_utc", "value")
    .sort("day_utc")
    .collect()
)

print(mvrv.head())
```

**Several metrics wide (pivot)**

```python
import polars as pl

metrics = ["market_cap", "supply_btc", "mvrv"]

wide = (
    pl.scan_parquet("brk_metrics.parquet")
    .filter(pl.col("metric").is_in(metrics))
    .collect()
    .pivot(values="value", index="day_utc", on="metric")
    .sort("day_utc")
)

print(wide.tail())
```

**Coverage for selected metrics**

```python
import polars as pl

metrics = ["market_cap", "supply_btc", "mvrv"]

coverage = (
    pl.scan_parquet("brk_metrics.parquet")
    .filter(pl.col("metric").is_in(metrics))
    .group_by("metric")
    .agg(
        pl.len().alias("rows"),
        pl.col("day_utc").min().alias("first_day"),
        pl.col("day_utc").max().alias("last_day"),
    )
    .sort("metric")
    .collect()
)

print(coverage)
```

## StackSats runtime projection (optional)

StackSats strategy entry points often use a derived wide parquet with columns such as `date`, `price_usd`, and selected features. To build that from this long-format file, filter to the metrics your strategy needs, pivot by `day_utc`, rename `day_utc` to `date`, and derive `price_usd = market_cap / supply_btc` if both inputs are present.

## Fetching data with the StackSats CLI (optional)

If you install StackSats and prefer it to fetch and verify data:

```sh
stacksats data fetch
stacksats data prepare
stacksats data doctor
```

Typical behavior: download source data under `~/.stacksats/data/brk/`, write `bitcoin_analytics.parquet` under `~/.stacksats/data/`, and verify hashes and sizes from the project manifest. Follow the current StackSats docs for release-specific details.

## Suggested workflow (students)

1. Choose a small set of metrics (e.g. `market_cap`, `supply_btc`, `mvrv`).
2. Filter the long-format table to those `metric` values.
3. Pivot to wide format if you want one column per series for plots or models.
4. Check first and last `day_utc` per metric before comparing periods.
5. When a name is opaque, use the [taxonomy](https://hypertrial.github.io/stacksats/reference/merged-metrics-taxonomy/) and [data guide](https://hypertrial.github.io/stacksats/reference/merged-metrics-data-guide/).
