# V2 Backtest — Walk-Forward Results

One notebook. Drop at project root, run. Results below are from the actual run on real data.

## File 

`v2_defensible_backtest.ipynb` — single deliverable. Adds MVRV + momentum gate + front-loading + regime overlay on top of Mig's baseline. Walk-forward validated.

## Headline result

| Fold | Baseline | V2 (tuned) | Improvement |
|---|---|---|---|
| **Training fold (2018-2022)** | 58.31% | **64.44%** | **+6.13pp** |
| **Test fold (2023-2025, held out)** | 56.67% | **54.84%** | **-1.83pp** |
| Full backtest (2018-2025) | 53.18% | 58.93% | +5.75pp |

**Honest verdict:** V2 improved the training fold meaningfully but did **not** generalize to the held-out test fold. The notebook's own diagnostic prints "Generalization: FAILED" — the strategy overfits to 2018-2022.

**Bootstrap 95% CI on test fold:** [-15.02, +10.61]pp — the confidence interval includes zero, so the test-fold change is **not statistically significant**.

## What actually worked: the 2022 fix

MVRV did exactly what it was designed to do for 2022:

| Year | Baseline mean excess | V2 mean excess | Δ |
|---|---|---|---|
| 2018 | +0.58 | +0.98 | +0.40 |
| 2019 | +1.39 | +0.84 | -0.55 |
| 2020 | -0.12 | +3.28 | +3.40 |
| 2021 | +5.06 | +1.92 | -3.14 |
| **2022** | **-2.67** | **-0.38** | **+2.29** ✅ |
| **2023** | **+0.35** | **-1.98** | **-2.33** ❌ |
| 2024 | +2.69 | +4.32 | +1.63 |

**2022 win rate went from 20.8% → 55.1%** — the bear-market falling-knife problem was fixed by MVRV exactly as the diagnosis predicted.

**But the same MVRV multiplier hurt 2023:** when BTC stayed low through 2023 H1 before rallying, MVRV said "keep buying" but the cheapest day was day 1 of the window. The fix that helped 2022 hurt 2023 by the same mechanism, just with opposite price direction.

## Ablation: MVRV is doing all the work

| Component disabled | Score | Drop |
|---|---|---|
| Full v2 | 58.94% | — |
| **No MVRV** | **45.46%** | **-13.47pp** |
| No regime | 57.38% | -1.55pp |
| No front-load | 57.71% | -1.23pp |
| No momentum gate | 58.94% | 0.00pp |

MVRV drives essentially all the score gain on the full backtest. Front-loading and the regime overlay contribute little. The momentum gate contributes nothing as currently tuned.

## What to report to the supervisor

Three honest paragraphs:

**1. The diagnosis was correct.** From the original metrics.json, the 2022 windows lost 2.67pp on average. V2 attacked this with on-chain MVRV. The 2022 fix worked: mean excess improved from -2.67 to -0.38, win rate from 21% to 55%.

**2. The fix did not generalize.** Walk-forward validation (train 2018-2022, test 2023-2025) showed the held-out test fold lost 1.83pp. The MVRV multiplier that helped the 2022 bear market hurt 2023's stay-low-then-rally pattern. Bootstrap 95% CI on the test fold includes zero.

**3. What this tells us.** The full-backtest gain (+5.75pp) is real but not generalizable — it's earned by a parameter setting that was tuned on the years it then scored well on. This is the textbook definition of overfitting, and the walk-forward design caught it. The honest score number for the supervisor is the test-fold number (-1.83pp), not the full-backtest number.

## What v2 does NOT do

- Does **not** edit `template/model_development_template.py`. All changes are applied via monkey-patch in the notebook so Mig's branch stays clean.
- Does **not** use a daily Polymarket sentiment signal. The BiLSTM/FinBERT classifier was used for validating the contrarian inversion hypothesis (separately reported in the NLP module), not as a daily DCA input. Polymarket trade data doesn't cover 2022, so a sentiment-based fix wouldn't help the year that's the biggest score drag anyway.

## Framework finding (worth flagging to Mig)

`allocate_sequential_stable` (the lock-on-compute normalization) is only sensitive to **within-window relative changes**, not absolute signal levels. A constant multiplier across the full window is cancelled by the running-mean normalization. This means:

- The MVRV multiplier helps most when MVRV is *changing* through the window (the 2022 bottom forming), less when MVRV is flat-cheap for the entire year (which is part of why 2023 hurt)
- Front-loading had to be implemented as a post-normalization weight tilt, not a raw-signal multiplier (the first version used a raw multiplier and got zero effect)

This has implications for how any future signals get integrated.

## Best parameters from random search

```
mvrv_alpha          = 0.296
mvrv_clip           = 0.35
dd_default          = 1.8
mstr_alpha          = 0.5
momentum_gate       = False
front_load          = True
front_load_days     = 45
front_load_tilt     = 0.15
use_regime          = True
regime_up_dampen    = 0.3
regime_down_amp     = 1.0
```

## Possible next steps

1. **More conservative MVRV** — drop `mvrv_alpha` to ~0.10 and `mvrv_clip` to 0.20, so the multiplier moves weights less aggressively. Might give a smaller but generalizable gain.
2. **Gated MVRV** — only fire the MVRV bonus when both MVRV is low AND 30-day momentum has turned positive (catches the bottom-confirming inflection, not the prolonged-cheap period that hurts 2023).
3. **Multi-fold CV** — instead of one train/test split, do 3-fold CV across the period to find params that work across multiple bear/bull regimes, not just 2018-2022.
4. **Accept the trade-off** — present the 2022 fix as a research finding, not a score-gain claim. Frame as "MVRV demonstrably helps bear-market windows but at the cost of stay-low-then-rally windows" — that's an honest empirical contribution.

## How to run

1. Drop `v2_defensible_backtest.ipynb` at the project root (same level as `template/` and `data/`)
2. Open in Jupyter
3. Run all cells top to bottom
4. Wait ~25-30 minutes (the random search in cell 11 is the bottleneck)

To shorten: set `N_TRIALS = 60` in cell 11 (default 120).

## Outputs

All saved to `output/v2/`:

| File | Content |
|---|---|
| `summary.json` | All metrics, best params, bootstrap CIs |
| `random_search_trials.csv` | Every random-search trial |
| `ablation.csv` | Ablation results |
| `headline.svg` | The 4-panel slide-deck shot |
| `yearly_breakdown.svg` | Before/after by year (the 2022 fix detail) |
| `bootstrap_ci.svg` | Bootstrap CI distribution comparison |
| `mvrv_context.svg` | MVRV historical context |
| `mvrv_2022.svg` | 2022 BTC vs MVRV detail |
| `ablation.svg` | Component ablation chart |
