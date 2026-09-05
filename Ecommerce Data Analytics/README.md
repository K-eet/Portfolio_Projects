# E-Commerce Analytics: End-to-End Data Pipeline

## Business Context
Analyzed a UK-based online retail dataset containing **541,909 transactions** spanning December 2010 to December 2011. The business primarily sells unique all-occasion gifts to both retail and wholesale customers across 38 countries.

## Project Objective
Build a comprehensive analytics pipeline to uncover customer purchasing patterns, identify
high-value segments, and provide actionable insights for business growth - then push past
description into a decision: **which customers are about to stop buying, and is it worth
spending money to keep them?**

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python get_data.py               # downloads the dataset -> data.csv (no login needed)
jupyter lab                      # run notebooks 1 -> 6 in order
```

The `.csv` files are generated (not committed): `get_data.py` creates `data.csv`, then
the notebooks produce `clean_data.csv` and `data_final.csv` as you run them in order.

## Key Skills Demonstrated

| Category | Skills |
|----------|--------|
| **Data Engineering** | ETL pipeline design, data cleaning, feature engineering |
| **Python** | Pandas, data wrangling, regex pattern matching, aggregations |
| **Data Visualization** | Matplotlib, Seaborn |
| **Statistical Analysis** | Descriptive statistics, distribution analysis, segmentation |
| **Business Analytics** | CLV modeling, customer segmentation, trend analysis |
| **Churn Modelling** | Label definition, leakage-safe temporal splits, logistic regression |
| **Decision Analysis** | Cost-weighted thresholds, expected-value ranking, benchmarking vs no model |

## Pipeline Architecture

```
Raw Data (541K rows)
        |
        v
[1. Data Cleaning] --> Removed nulls, duplicates, invalid codes
        |                (~400K clean records)
        v
[2. Feature Engineering] --> Created 10+ derived features
        |                     (CLV, RFM metrics, time features)
        v
[3. Exploratory Data Analysis] --> Statistical analysis & visualizations
        |
        v
[4. Define Churn] --> No churn label exists in retail; one is derived
        |               from observed purchase spacing (90 days)
        v
[5. Time Split + Baseline] --> Leak-free snapshot, logistic regression
        |                        (AUC 0.744)
        v
[6. Cost & Benchmark] --> Price the two errors, benchmark against
                            the no-model rule
```

## Detailed Methodology

### 1. Data Cleaning & Preprocessing
- **Missing Values**: Dropped rows with null CustomerID (critical for customer analysis)
- **Duplicates**: Removed duplicate transactions
- **Data Type Corrections**:
  - Converted InvoiceDate to datetime
  - Cast CustomerID from float to integer
- **Invalid Records**: Filtered out non-standard StockCodes (POSTAGE, MANUAL, DISCOUNT, etc.)
- **Result**: 399,689 clean records retained

### 2. Feature Engineering

Created actionable business metrics:

| Feature | Description | Business Use |
|---------|-------------|--------------|
| `TotalAmount` | Quantity x UnitPrice | Order value analysis |
| `PriceCategory` | Low/Medium/High (quantile-based) | Price sensitivity analysis |
| `ProductPopularity` | Total quantity sold per product | Inventory optimization |
| `CustomerLifetimeValue` | Total spend per customer | Customer prioritization |
| `AvgOrderValue` | Mean transaction value per customer | Segment profiling |
| `PurchaseFrequency` | Number of unique invoices per customer | Loyalty identification |
| `IsReturningCustomer` | Binary flag for repeat purchasers | Retention analysis |
| `DayOfWeek`, `Month`, `IsWeekend` | Temporal features | Demand forecasting |
| `MonthlySalesTrend` | Aggregated monthly revenue | Trend identification |

### 3. Exploratory Data Analysis

*Figures below are printed by `3. EDA.ipynb`, which runs on `data_final.csv` (391,150 sales-only transactions, 4,334 customers).*

**Customer segmentation** — customers split on median spend and median order count:

| Segment | Customers | % of customers | % of revenue | Avg CLV |
|---|---|---|---|---|
| **Champions** (high spend, high frequency) | 1,765 | 40.7% | **83.6%** | £4,139 |
| **At Risk** (low spend, low frequency) | 1,765 | 40.7% | 5.8% | £289 |
| Big Spenders (high spend, low frequency) | 402 | 9.3% | 8.6% | £1,859 |
| Loyal (low spend, high frequency) | 402 | 9.3% | 2.0% | £434 |

Two-fifths of customers produce 84% of revenue, and the equally sized At Risk group produces 5.8%.

**Retention is the dominant effect.** Returning customers average **£2,867 against £416** for
one-time buyers — **6.9x more valuable** — and generate **92.8% of revenue** from 65.3% of
customers.

**Geographic:**
- UK is **82.9%** of revenue (£7.24M of £8.74M); international is 17.1%
- Highest average order value: **Netherlands (£3,053)**, **Australia (£2,466)**, **Japan (£1,969)**
  — each on a small base of 8-9 customers, so read these as leads to investigate, not as proven
  markets. Singapore and Lebanon show higher AOV still on a single customer each, and are excluded
  for that reason.

**Temporal:**
- Revenue peaks **September to November** (£939K, £1,002K, £1,137K) against a ~£600K baseline —
  the Christmas gift build-up. December 2011 looks like a collapse only because the data stops on
  the 9th.
- **Weekdays take 91.1%** of revenue against 8.9% at weekends (the business is closed Saturdays)

**Products:**
- Pareto holds: the top **21.4% of products (783 of 3,659) generate 80% of revenue**
- Medium and high-priced items account for **77.8%** of revenue between them

### 4-6. Churn: defining it, predicting it, and pricing it

Retail is **non-contractual** — nobody cancels, they just stop coming back — so the dataset
contains no churn label and one has to be built. That makes up the second half of the project,
and the modelling is the least interesting part of it.

**Defining churn (notebook 4).** The threshold was set from how customers actually space their
purchases, not from a round number. Pooled inter-purchase gaps run to a median of 28 days, but
each customer's *own* median gap runs to 52 days — pooling over-weights frequent buyers, so the
per-customer view is the fair one. **90 days** of silence sits just below the 75th percentile of
those, making it genuinely unusual behaviour while still leaving time to act.

**Avoiding leakage (notebook 5).** Churn is *defined* by silence at the end of the data, so
computing recency over the whole dataset and then splitting randomly hands the model the answer
inside the question. Instead the timeline is cut at a snapshot date `C = end_date − 90`: features
come only from before `C`, the label only from after it, with runnable assertions that fail the
notebook if either window is violated. A plain logistic regression on six RFM-style features
reaches **AUC 0.744** — real signal, modest strength, and about what honest RFM features should
give. A much higher number would suggest the leak was still there.

**Pricing the errors (notebook 6).** AUC measures ranking quality and says nothing about whether
acting on the ranking makes money, so the two errors are costed: a false positive costs one
contact (assumed £3), a false negative costs the customer's forward value (their own historical
run-rate over a 90-day window). Under those assumptions the median customer's break-even churn
probability is **2.3%, not 50%** — the conventional cut-off misprices the decision by roughly
twentyfold.

## The result

**With an unlimited contact budget, the model is worth nothing.** Benchmarked against the
no-model rule — *contact everyone silent for R days*, with **R swept too**, because comparing a
tuned model against an untuned rule is a rigged fight — the model wins by **£136 across 587
customers, about £0.23 each.** No business should maintain a model, a feature pipeline and a
retraining schedule for that. The finding holds across every combination of contact cost (£1–£25)
and save rate (10–40%) tested.

**Under a realistic contact budget, it depends entirely on how the model is used.** Given capacity
for 100 customers:

| Ranking used to pick the 100 | Median EV over 30 splits |
|---|---|
| **predicted probability × value at risk** | **£7,132** |
| value at risk alone (no model) | £4,956 |
| recency — the no-model rule | £4,022 |
| random | £3,198 |
| predicted probability alone | £2,881 |

Two things there matter more than the AUC. **Ranking by churn probability alone is worse than
choosing customers at random** — the people most likely to lapse are the small, infrequent ones,
so a scarce budget spent on them protects very little money, and no accuracy metric reveals this.
And the model only earns its keep **once its output is multiplied by what each customer is
worth**, at which point it beats the rule in 25 of 30 splits by a median £3,233.

The practical read: if the budget is unconstrained, use the rule and skip the model. If it is
constrained, use the model — but rank by expected value, never by probability.

## Key Business Insights

1. **Customer Retention is Critical**: Returning customers generate 92.8% of revenue and are worth 6.9x a one-time buyer - invest in loyalty programs. *Notebooks 4-6 take this from an observation to a costed decision.*
2. **Geographic Expansion**: High-AOV countries (Netherlands, Australia, Japan) present untapped potential
3. **Seasonal Planning**: Allocate inventory and marketing budget for Q4 peak season
4. **Product Strategy**: Focus on medium/high price point items, which drive 77.8% of revenue; 21.4% of the catalogue produces 80% of it
5. **Segment-Specific Marketing**: Target Low CLV/Low Frequency segment with re-engagement campaigns

## Files

| File | Description |
|------|-------------|
| `1. data_cleaning.ipynb` | Data preprocessing and quality checks |
| `2. feature_engineering.ipynb` | Feature creation and validation |
| `3. EDA.ipynb` | Exploratory analysis with visualizations |
| `4. define_churn.ipynb` | Deriving a churn label from purchase spacing |
| `5. time_split.ipynb` | Leak-free temporal snapshot and baseline model |
| `6. cost_and_benchmark.ipynb` | Cost-based evaluation and the no-model benchmark |
| `Theory.md` | Plain-language walkthrough of the churn reasoning |
| `get_data.py` | Downloads the source dataset (no login needed) |
| `data.csv` | Source dataset, as downloaded (generated) |
| `clean_data.csv` | Cleaned dataset (generated) |
| `data_final.csv` | Final dataset with engineered features (generated) |

## Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=flat)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=flat)

## Data Source

[UCI Machine Learning Repository / Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) - Online Retail Dataset
