# EV Financial Health & Investment Analysis
### Tesla vs BYD vs Ford (2022–2024)

A comparative fundamental analysis of three automotive archetypes navigating the EV
transition — from raw data collection through to a structured investment view and
valuation. The goal is not a buy/sell call, but to demonstrate the full analytical
workflow: pull the data, compute the right metrics, interpret them, and form a
defensible, valuation-backed thesis.

## Headline Finding

The market is paying **~188x earnings for Tesla** and **~2.4x for BYD** — despite BYD
generating roughly **10x the free cash flow** (~$36B vs ~$3.6B in 2024) and converting
earnings to cash more reliably. The gap is a function of growth expectations and a
geopolitical risk premium, not current financial performance. Tesla's headline
profitability still leads, but it is compressing toward legacy-automaker levels while
its multiple is not.

## Companies

| Company | Ticker | Archetype |
|---------|--------|-----------|
| **Tesla** | TSLA | Pure-play EV, high-margin pioneer under price-war pressure |
| **BYD** | BYDDY | Chinese EV giant, volume-driven, heavy capex phase |
| **Ford** | F | Legacy automaker funding an EV transition from its ICE profits |

## Repository Structure

The analysis runs as a pipeline — each notebook consumes the output of the previous one.

| Notebook | Purpose |
|----------|---------|
| [`01_data_collection.ipynb`](notebooks/01_data_collection.ipynb) | Pull income statement, balance sheet, and cash flow from yfinance; compute core metrics; clean partial/NaN years; persist to pickle. |
| [`02_visualization.ipynb`](notebooks/02_visualization.ipynb) | Plotly dashboard tracking Net Profit Margin, Free Cash Flow, and ROA across all three companies. |
| [`03_deep_dive.ipynb`](notebooks/03_deep_dive.ipynb) | Year-over-year change analysis and earnings-quality check via Cash Conversion Ratio (OCF / Net Income). |
| [`04_investment_thesis.ipynb`](notebooks/04_investment_thesis.ipynb) | Structured investment view using the **SCIR framework** (Situation, Complication, Implication, Risk), each thesis tied to specific data points, plus a comparative ranking. |
| [`05_valuation.ipynb`](notebooks/05_valuation.ipynb) | Valuation layer: P/E, FCF Yield, and EV/EBITDA computed from year-end market caps. Connects fundamentals to price. |

## Metrics & Methodology

**Profitability & efficiency**
- Net Profit Margin = Net Income / Total Revenue
- Return on Assets = Net Income / Total Assets
- Free Cash Flow (as reported by yfinance)

**Earnings quality**
- Cash Conversion Ratio = Operating Cash Flow / Net Income — a ratio below 1 means a
  company reports more profit than it generates in cash (a red flag).

**Valuation**
- P/E = Market Cap / Net Income
- FCF Yield = Free Cash Flow / Market Cap
- EV/EBITDA = (Market Cap + Total Debt − Cash) / EBITDA

Market caps use share price on the last trading day of each fiscal year × shares
outstanding (Share Issued).

**Analytical framework:** Each company thesis follows **SCIR** — *Situation* (what the
data shows), *Complication* (what's driving it), *Implication* (what it means for an
investor, including variant perception), and *Risk* (what would falsify the view).

## Key Findings (2024)

| Metric | Tesla | BYD | Ford |
|--------|------:|----:|-----:|
| Net Profit Margin (%) | 7.3 | 5.2 | 3.2 |
| Return on Assets (%) | 5.8 | 5.1 | 2.1 |
| Free Cash Flow ($B) | 3.6 | 36.1 | 6.7 |
| Cash Conversion Ratio | 2.09 | 3.32 | 2.62 |

- **Tesla** — Margin compression from a deliberate price war; NPM and ROA roughly halved
  from 2022. Top or bottom on every dimension, no middle ground. Highest profitability,
  weakest cash profile relative to its valuation.
- **BYD** — The most balanced financial profile and strongest cash generator, but FCF
  and CCR are declining as it spends aggressively on capacity. The thesis hinges on
  whether the capex bet pays off before cash generation deteriorates.
- **Ford** — A genuine turnaround from a low base (NPM −1.3% → 3.2%), but aggregate
  numbers mask a profitable ICE business (Ford Blue/Pro) subsidizing a loss-making EV
  division (Model e). No variant perception working in its favor — the market sees Ford
  accurately.

## Data & Limitations

- **History:** yfinance free tier returns ~4 years of annual fundamentals; after
  removing the partial current year and NaN rows, the analysis covers **2022–2024**.
  Sufficient to capture the EV-transition trend, but a small sample for trend claims.
- **Fiscal year:** All three companies are assumed to report on a calendar-year basis.
  The partial-year filter uses the current calendar year as the cutoff and would need
  adjustment for non-December fiscal year ends.
- **Future improvement:** Supplement with SEC EDGAR / SimFin to extend history and move
  to quarterly granularity for a fuller pre/post-EV-boom comparison.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Run the notebooks in order (`01` → `05`). Notebook 01 must run first — it produces the
`data/metrics.pkl` and `data/raw_data.pkl` files the later notebooks load.

## Tech Stack

Python · pandas · yfinance · Plotly · Jupyter

---

*Author: Lee Keet Men*
