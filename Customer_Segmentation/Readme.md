# Customer Segmentation & Targeting Analysis

## Business Problem
A supplier needed to identify the **top 100 high-value customers** to target for a Coca-Cola sales campaign. The challenge was to analyze transaction data across multiple product categories and pinpoint customers with the highest purchasing potential in the sugary drinks segment.

## Solution Overview
Developed a data-driven customer segmentation model using Python to analyze 116,000+ transactions and identify the most valuable customer targets based on historical purchasing behavior.

## Key Skills Demonstrated

| Category | Skills |
|----------|--------|
| **Data Analysis** | Exploratory data analysis, customer segmentation, sales analysis |
| **Python** | Pandas, data wrangling, aggregation functions, merging datasets |
| **Data Visualization** | Tableau dashboard design, interactive reporting |
| **Business Intelligence** | Customer lifetime value analysis, targeting recommendations |

## Methodology

### 1. Data Exploration
- Loaded and profiled dataset with 116,338 transactions across 13 variables
- Analyzed data types, missing values, and unique categories
- Identified 8 product categories including Sugary Drinks, Energy Drinks, Dairy, etc.

### 2. Customer Value Analysis
- Filtered transactions to focus on the 'Sugary Drinks' category (most relevant for Coca-Cola)
- Aggregated sales by customer to calculate total spend
- Ranked customers by cumulative sales amount in descending order

### 3. Target Customer Identification
- Selected top 100 customers with highest sugary drinks purchases
- Sales range: Top customer spent $407,960 vs. $4,128 for 100th customer
- Merged customer names back into final dataset for actionable output

### 4. Visualization & Reporting
- Created Tableau dashboard for stakeholder presentation
- Exported clean CSV with Customer ID, Name, and Total Sales Amount

## Key Findings

- **Top Customer Value**: $407,960 in sugary drinks purchases
- **Top 100 Threshold**: Minimum $4,128 in sales to qualify
- **Customer Concentration**: High-value customers show significant spend concentration, making targeted campaigns cost-effective

## Files

| File | Description |
|------|-------------|
| `Most_Valuable_Customers.ipynb` | Python analysis notebook with documented methodology |
| `Dashboard.twbx` | Tableau dashboard for visual exploration |
| `Most_Valuable_Customers.csv` | Output: Top 100 customers for targeting |
| `Data.csv` | Source transaction data |
| `Task_Brief.pdf` | Original business requirements |

## Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-E97627?style=flat&logo=tableau&logoColor=white)

## Business Impact

This analysis enables:
- **Focused Marketing**: Target high-value customers with personalized Coca-Cola campaigns
- **Resource Optimization**: Concentrate sales efforts on customers with proven purchase history
- **Data-Driven Decisions**: Replace intuition-based targeting with quantifiable customer rankings
