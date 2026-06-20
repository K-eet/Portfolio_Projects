# Project Status: EV Financial Health & Investment Analysis

## What This Is
Comparative fundamental analysis of Tesla, BYD, and Ford navigating the EV transition.
Repo: github.com/K-eet/Portfolio_Projects (Financial Analysis directory)

## Completed (Phase 1 — Annual Analysis)
- **01_data_collection.ipynb**: yfinance pull, metrics calc, cleaning, pickle save
- **02_visualization.ipynb**: Plotly dashboard (NPM, FCF, ROA)
- **03_deep_dive.ipynb**: YoY change, Cash Conversion Ratio earnings quality
- **04_investment_thesis.ipynb**: SCIR framework per company + comparative ranking
- **05_valuation.ipynb**: P/E, FCF Yield, EV/EBITDA with point-in-time market caps
- **metrics.py** + **test_metrics.py**: tested calculation module (10 pytest cases passing)
- Clean README, .gitignore, requirements.txt

## In Progress (Phase 2 — Quarterly Data via SEC EDGAR)
Building quarterly granularity for Tesla and Ford (BYD stays annual — foreign 
private issuer, files 20-F annually, no 10-Q quarterly reports exist).

**edgar_utils.py** — all extraction logic, covered by 17 pytest cases in
**test_edgar_utils.py**:
- `get_company_facts(cik)` — pulls XBRL JSON from data.sec.gov (no API key needed)
- `get_full_metric_history(facts, concept)` — discrete-quarter income-statement
  metrics; reconstructs Q4 via Annual(10-K) − Q1 − Q2 − Q3, but only for years where
  a discrete Q4 isn't already reported (fixes earlier double-counted Dec-31 rows)
- `get_ytd_flow_history(facts, concept)` — cash-flow metrics, which are reported
  year-to-date; recovers discrete quarters by differencing cumulative periods
- `get_instant_metric_history(facts, concept)` — balance-sheet "instant" snapshots
- `get_merged_metric_history(facts, concepts)` — spans tag migrations (e.g. revenue)

**CIKs**: Tesla 1318605, Ford 37996

**Metric → tag → extraction method** (verified for both companies):
- Net Income: `NetIncomeLoss` → full
- Revenue: `Revenues` + `RevenueFromContractWithCustomerExcludingAssessedTax` (ASC 606
  migration) → merged
- Operating Cash Flow: `NetCashProvidedByUsedInOperatingActivities` → ytd
- Capex: Tesla `PaymentsToAcquirePropertyPlantAndEquipment` /
  Ford `PaymentsToAcquireProductiveAssets` → ytd
- Assets: `Assets` → instant

Extraction is wired into **01_data_collection.ipynb** (Phase 2 section) and saved as a
tidy long DataFrame `[company, metric, end, val]` (599 rows) to
**data/quarterly_edgar.pkl**. The notebook section is annotated for portfolio readers:
a flow-vs-stock / discrete-vs-cumulative conceptual frame, inline design rationale on the
dispatch-by-reporting-shape extractor, a reconciliation **validation cell** (four
reconstructed quarters must sum to the reported annual; 2018+ window reconciles to 0.00%),
and a decisions/data-quality log.

**Data-quality finding (documented, not a bug):** Ford's FY2013 `NetIncomeLoss` is tagged
$7.16B in its original 2013 10-K but $11.95B in a comparative column of the 2015 10-K.
Keeping the latest-filed value (correct for restatements) picks up that re-tag, so it
disagrees with the original filing and Ford's own quarters. It predates the analysis window
and no reconstruction depends on it (2013 Q4 is reported directly), so validation surfaces it
informationally and asserts hard only on 2018+.

## Resolved
1. ~~Assets instant concept~~ — `get_instant_metric_history` added (flow vs stock:
   balance-sheet items are point-in-time, no Q4 reconstruction).
2. ~~OCF short history~~ — root cause was *not* a tag swap but year-to-date reporting;
   `get_ytd_flow_history` differences cumulative periods. Tesla 13→50 quarters, Ford 9→37.
3. ~~Ford Capex missing~~ — Ford uses `PaymentsToAcquireProductiveAssets`.
4. Latent bug found + fixed: `get_full_metric_history` double-counted Q4 whenever a
   10-K reported a discrete Q4 (had affected Net Income in the annual pipeline too).

## Remaining
- **Currency**: BYD reports in RMB/CNY — needs conversion if ever integrated at quarterly
  level (BYD currently excluded from quarterly — no 10-Q filings exist regardless).

## Architecture Principle
Reusable logic lives in .py modules (metrics.py, edgar_utils.py), tested with pytest.
Notebooks orchestrate and visualize, they don't contain core logic.
Exploration/verification work goes in 00_edgar_exploration.ipynb, kept separate from 
the clean 01-05 pipeline.