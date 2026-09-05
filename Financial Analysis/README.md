# EV Financial Health & Investment Analysis
### Tesla vs BYD vs Ford (2022–2024)

A comparative fundamental analysis of three automotive archetypes navigating the EV
transition — from raw filings through to a structured investment view and valuation. The
goal is not a buy/sell call, but to demonstrate the full analytical workflow: pull the
data, compute the right metrics, interpret them, and form a defensible thesis.

## Headline Finding

**The market pays about 189x earnings for Tesla, 18x for BYD and 6x for Ford — and Tesla
generates the least free cash flow of the three.** Ford produces $6.7B, BYD $5.0B, Tesla
$3.6B. Over 2022–2024 Tesla's net margin halved (15.4% → 7.3%) and its revenue growth fell
to 0.9% in 2024, while BYD grew revenue 72% with margins rising every year.

The 31-fold valuation spread is not explained by current financial performance. It is a
claim about Tesla's future — FSD, Optimus, energy storage — none of which appears in these
statements, and a geopolitical discount applied to BYD that the financials do not support
on their own.

## Companies

| Company | Ticker | Archetype |
|---------|--------|-----------|
| **Tesla** | TSLA | Pure-play EV, high-margin pioneer under price-war pressure |
| **BYD** | BYDDY | Chinese EV giant, volume-driven, fastest-growing of the three |
| **Ford** | F | Legacy automaker funding an EV transition from its ICE profits |

## Key Findings (FY2024, all USD)

| Metric | Tesla | BYD | Ford |
|--------|------:|----:|-----:|
| Net Profit Margin (%) | 7.3 | 5.2 | 3.2 |
| Return on Assets (%) | 5.8 | 5.2 | 2.1 |
| Free Cash Flow ($B) | 3.6 | 5.0 | 6.7 |
| Cash Conversion Ratio | 2.10 | 3.32 | 2.62 |
| Revenue growth 2022→2024 (%) | +19.9 | +71.6 | +17.0 |
| P/E | 189.3 | 17.5 | 6.0 |
| FCF Yield (%) | 0.3 | 5.1 | 19.1 |
| EV/EBITDA | 91.1 | 5.5 | 12.2 |

- **Tesla** — Deliberate margin compression from the 2023 price war. Net margin and return
  on assets both roughly halved (−8.2pp and −9.4pp), the latter falling further because the
  asset base grew 48% while net income fell 44%. Highest margin in the set, lowest free cash
  flow, and the highest price on every multiple.
- **BYD** — The only company compounding: +72% revenue, margins and returns rising every
  year, and the strongest cash conversion of the three at 3.32, priced at 18x earnings. Its
  falling CCR (8.47 → 3.32) is convergence towards a normal manufacturing range, not
  deterioration — net income grew 127% while operating cash flow fell 11%.
- **Ford** — A genuine recovery from a 2022 loss (net margin −1.3% → 3.2%) and the largest
  absolute cash generator. Cheapest on P/E and FCF yield, but only mid-pack on EV/EBITDA:
  $160.9B of debt against a $35.2B market cap, almost all of it Ford Credit's lending book.
  The equity is cheap; the enterprise is not.

Aggregate figures also mask Ford's segment split — a profitable ICE business (Ford Blue,
Ford Pro) subsidising a loss-making EV division (Model e).

## Repository Structure

The analysis runs as a pipeline — each notebook consumes the output of the previous one.

| Notebook | Purpose |
|----------|---------|
| [`01_data_collection.ipynb`](notebooks/01_data_collection.ipynb) | Pull annual fundamentals from SEC EDGAR (Tesla, Ford) and yfinance (BYD); translate BYD from CNY to USD; assemble one USD table. Appendix: quarterly XBRL reconstruction with reconciliation testing. |
| [`02_visualization.ipynb`](notebooks/02_visualization.ipynb) | Dashboard tracking net profit margin, free cash flow and return on assets across all three. |
| [`03_deep_dive.ipynb`](notebooks/03_deep_dive.ipynb) | Revenue growth, year-on-year change in percentage points, and earnings quality via cash conversion. |
| [`04_investment_thesis.ipynb`](notebooks/04_investment_thesis.ipynb) | Structured investment view using the **SCIR framework** (Situation, Complication, Implication, Risk), each thesis tied to specific data points, plus a comparative ranking. |
| [`05_valuation.ipynb`](notebooks/05_valuation.ipynb) | P/E, FCF yield and EV/EBITDA from year-end market caps. Connects fundamentals to price. |

| Module | Purpose |
|--------|---------|
| [`config.py`](config.py) | Analysis window, company identifiers, reporting currencies. One source of truth so no notebook defines its own cutoff. |
| [`edgar_utils.py`](edgar_utils.py) | SEC XBRL extraction — one extractor per reporting shape (discrete flow, YTD flow, instant stock, merged tags). |
| [`fx.py`](fx.py) | CNY→USD translation: average rate for flows, year-end rate for balance-sheet stocks. |
| [`metrics.py`](metrics.py) | Metric formulas, shared across notebooks so they cannot drift. |

Tests: `test_edgar_utils.py`, `test_fx.py`, `test_metrics.py` — run with `pytest`.

## Data Sources

**SEC EDGAR XBRL** (`data.sec.gov`) is the primary source for Tesla and Ford: as-filed 10-K
figures, full history, no vendor normalisation between the filing and the analysis.

**yfinance** covers three gaps EDGAR cannot fill:

1. **BYD files nothing financial with the SEC.** Its only EDGAR presence (CIK 1445162) is
   ADR registration paperwork — `F-6EF`, `F-6 POS`, `424B3` — filed by the depositary bank.
   There is no 20-F, no 10-K, and `companyfacts` returns 404. This is a hard limit.
2. **EDGAR publishes filings, not quotes.** Market capitalisation needs a share price.
3. **EBITDA, total debt and share count are not comparably tagged.** Ford reports
   `DepreciationDepletionAndAmortization` as one annual line; Tesla splits the same
   economics across several tags. Ford's `LongTermDebtNoncurrent` is empty across this
   window. Building these per-filer from whichever tags each happens to use would not be
   the same measure twice, so all three come from yfinance's normalised aggregates — one
   consistent basis, at the cost of not being as-filed.

### The currency correction

**BYD reports in renminbi; its ADR trades in dollars.** An earlier version of this analysis
compared BYD's reported figures directly against Tesla's and Ford's, and divided a dollar
market cap by a renminbi net income. That overstated BYD's 2024 free cash flow as **$36.1B**
(it is ~$5.0B) and its P/E as **2.4x** (it is 17.5x), and led this README to claim BYD
generated "roughly 10x the free cash flow" of Tesla — wrong in magnitude and in direction,
since Ford generates more than either.

Every BYD figure is now translated to USD in notebook 01 before it reaches the analysis:
flows at the year's average rate, balance-sheet stocks at the year-end rate, following
standard translation practice. Notebook 01 asserts a currency sanity check that would have
caught the original defect.

## Metrics & Methodology

**Profitability & efficiency**
- Net Profit Margin = Net Income / Total Revenue
- Return on Assets = Net Income / Total Assets
- Free Cash Flow = Operating Cash Flow − Capex (derived, not taken from a vendor field)

**Earnings quality**
- Cash Conversion Ratio = Operating Cash Flow / Net Income — below 1 means a company reports
  more profit than it generates in cash. Not meaningful when net income is negative.

**Valuation**
- P/E = Market Cap / Net Income (undefined for a loss-making year)
- FCF Yield = Free Cash Flow / Market Cap
- EV/EBITDA = (Market Cap + Total Debt − Cash) / EBITDA

Market caps use the last close of each fiscal year × year-end share count.

**Analytical framework:** each thesis follows **SCIR** — *Situation* (what the data shows),
*Complication* (what's driving it), *Implication* (what it means, including variant
perception), *Risk* (what would falsify the view).

## Data & Limitations

- **Three years.** yfinance's free tier caps BYD at ~4 years of annual statements, and BYD
  is the binding constraint on a three-way comparison. EDGAR alone would give 15+ years for
  Tesla and Ford. A small sample for trend claims.
- **The window is fixed, not rolling.** `config.ANALYSIS_YEARS` is hard-coded. The written
  theses argue about these specific years, so the data must not shift underneath them when a
  new 10-K is filed. Extending the analysis means editing that list *and* re-reading the
  theses.
- **Fiscal year.** All three report to 31 December. The quarterly reconstruction relies on
  this and would need adjustment for a non-December year end.
- **BYD is single-sourced.** Its figures cannot be reconciled to a regulated filing the way
  Tesla's and Ford's can.
- **BYD's ROA carries a small translation effect.** Net income is translated at the average
  rate and total assets at the year-end rate, so the 2024 figure reads 5.22% against 5.14%
  as reported in renminbi. This is standard practice, not an error, but it is not a
  like-for-like ratio with Tesla's and Ford's.
- **EBITDA, debt and share count are vendor aggregates**, not as-filed — see Data Sources.
- **Not investment advice.** This excludes forward guidance, segment-level detail, product
  roadmaps and market context.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                          # 24 tests
jupyter lab
```

Run the notebooks in order (`01` → `05`). Notebook 01 must run first — it produces the
`data/fundamentals.pkl` that every later notebook loads.

Both data sources are free and need no API key. EDGAR requires a `User-Agent` header, set in
`edgar_utils.py`.

## Tech Stack

Python · pandas · SEC EDGAR XBRL API · yfinance · Plotly · pytest · Jupyter

---

*Author: Lee Keet Men*
