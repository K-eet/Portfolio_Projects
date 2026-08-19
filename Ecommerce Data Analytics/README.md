# E-Commerce Analytics: End-to-End Data Pipeline

## Business Context
Analyzed a UK-based online retail dataset containing **541,909 transactions** spanning December 2010 to December 2011. The business primarily sells unique all-occasion gifts to both retail and wholesale customers across 38 countries.

## Project Objective
Build a comprehensive analytics pipeline to uncover customer purchasing patterns, identify high-value segments, and provide actionable insights for business growth.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python get_data.py               # downloads the dataset -> data.csv (no login needed)
jupyter lab                      # run notebooks 1 -> 2 -> 3 in order
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

**Customer Segmentation Findings:**
- **High CLV & High Frequency**: 41.3% of customers (most valuable segment)
- **Low CLV & Low Frequency**: 42.5% of customers (opportunity for growth)
- Strong correlation between purchase frequency and lifetime value

**Geographic Insights:**
- UK accounts for majority of revenue (home market)
- **Highest Average Order Value**: Netherlands, Australia, Japan
- Expansion opportunity in high-AOV international markets

**Temporal Patterns:**
- Sales peak September through November (holiday season prep)
- Weekday sales significantly outperform weekends
- Returning customers drive the vast majority of revenue

**Product Analysis:**
- Distribution follows Pareto principle (80/20 rule)
- Small number of products drive majority of revenue
- Medium and high-priced items generate most sales

## Key Business Insights

1. **Customer Retention is Critical**: Returning customers generate the vast majority of revenue - invest in loyalty programs
2. **Geographic Expansion**: High-AOV countries (Netherlands, Australia, Japan) present untapped potential
3. **Seasonal Planning**: Allocate inventory and marketing budget for Q4 peak season
4. **Product Strategy**: Focus on medium/high price point items that drive most sales
5. **Segment-Specific Marketing**: Target Low CLV/Low Frequency segment with re-engagement campaigns

## Files

| File | Description |
|------|-------------|
| `1. data_cleaning.ipynb` | Data preprocessing and quality checks |
| `2. feature_engineering.ipynb` | Feature creation and validation |
| `3. EDA.ipynb` | Exploratory analysis with visualizations |
| `data.csv` | Original Kaggle dataset |
| `clean_data.csv` | Cleaned dataset |
| `data_final.csv` | Final dataset with engineered features |

## Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=flat)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=flat)

## Data Source

[UCI Machine Learning Repository / Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) - Online Retail Dataset
