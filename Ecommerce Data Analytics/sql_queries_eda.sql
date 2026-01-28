-- ============================================================================
-- E-Commerce Analytics SQL Queries
-- ============================================================================
-- Dataset: data_final.csv (UCI Online Retail Dataset)
-- Skills Demonstrated: CTEs, Window Functions, JOINs, Aggregations, Subqueries
-- ============================================================================

-- ============================================================================
-- 1. BASIC EXPLORATION
-- ============================================================================

-- Preview data structure
SELECT *
FROM data_final
LIMIT 10;

-- Dataset summary statistics
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT CustomerID) AS unique_customers,
    COUNT(DISTINCT InvoiceNo) AS unique_orders,
    COUNT(DISTINCT StockCode) AS unique_products,
    COUNT(DISTINCT Country) AS unique_countries,
    MIN(InvoiceDate) AS first_transaction,
    MAX(InvoiceDate) AS last_transaction,
    ROUND(SUM(TotalAmount), 2) AS total_revenue
FROM data_final;


-- ============================================================================
-- 2. TOP-SELLING PRODUCTS (with ranking)
-- ============================================================================

-- Using window function to rank products
WITH product_sales AS (
    SELECT
        StockCode,
        Description,
        SUM(TotalAmount) AS total_revenue,
        SUM(Quantity) AS total_units,
        COUNT(DISTINCT InvoiceNo) AS order_count,
        COUNT(DISTINCT CustomerID) AS customer_count
    FROM data_final
    GROUP BY StockCode, Description
)
SELECT
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    StockCode,
    Description,
    ROUND(total_revenue, 2) AS total_revenue,
    total_units,
    order_count,
    customer_count,
    ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS pct_of_total_revenue
FROM product_sales
ORDER BY total_revenue DESC
LIMIT 20;


-- ============================================================================
-- 3. CUSTOMER LIFETIME VALUE ANALYSIS (with RFM components)
-- ============================================================================

-- RFM Analysis using CTEs and Window Functions
WITH customer_metrics AS (
    SELECT
        CustomerID,
        MAX(InvoiceDate) AS last_purchase,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        SUM(TotalAmount) AS monetary,
        MIN(InvoiceDate) AS first_purchase,
        COUNT(DISTINCT DATE(InvoiceDate)) AS active_days
    FROM data_final
    GROUP BY CustomerID
),
rfm_scores AS (
    SELECT
        CustomerID,
        last_purchase,
        frequency,
        ROUND(monetary, 2) AS monetary,
        -- Recency score (1-4, higher is more recent)
        NTILE(4) OVER (ORDER BY last_purchase) AS r_score,
        -- Frequency score (1-4, higher is more frequent)
        NTILE(4) OVER (ORDER BY frequency) AS f_score,
        -- Monetary score (1-4, higher is more valuable)
        NTILE(4) OVER (ORDER BY monetary) AS m_score
    FROM customer_metrics
)
SELECT
    CustomerID,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CONCAT(r_score, f_score, m_score) AS rfm_segment,
    monetary AS total_spend,
    frequency AS order_count,
    CASE
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND m_score >= 3 THEN 'Big Spenders'
        WHEN r_score >= 3 THEN 'Recent Customers'
        WHEN f_score >= 3 THEN 'Frequent Buyers'
        WHEN m_score >= 3 THEN 'High Value'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'At Risk'
        ELSE 'Need Attention'
    END AS customer_segment
FROM rfm_scores
ORDER BY rfm_total DESC, monetary DESC;


-- Customer segment summary
WITH customer_metrics AS (
    SELECT
        CustomerID,
        MAX(InvoiceDate) AS last_purchase,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        SUM(TotalAmount) AS monetary
    FROM data_final
    GROUP BY CustomerID
),
rfm_scores AS (
    SELECT
        CustomerID,
        NTILE(4) OVER (ORDER BY last_purchase) AS r_score,
        NTILE(4) OVER (ORDER BY frequency) AS f_score,
        NTILE(4) OVER (ORDER BY monetary) AS m_score,
        monetary
    FROM customer_metrics
),
segmented AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'At Risk'
            ELSE 'Other'
        END AS segment
    FROM rfm_scores
)
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(SUM(monetary) * 100.0 / SUM(SUM(monetary)) OVER (), 1) AS pct_of_revenue,
    ROUND(AVG(monetary), 2) AS avg_clv
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;


-- ============================================================================
-- 4. GEOGRAPHIC ANALYSIS
-- ============================================================================

-- Country performance with ranking
WITH country_metrics AS (
    SELECT
        Country,
        SUM(TotalAmount) AS total_revenue,
        COUNT(DISTINCT CustomerID) AS unique_customers,
        COUNT(DISTINCT InvoiceNo) AS total_orders,
        SUM(Quantity) AS total_units
    FROM data_final
    GROUP BY Country
)
SELECT
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    Country,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS pct_of_revenue,
    unique_customers,
    total_orders,
    ROUND(total_revenue / NULLIF(total_orders, 0), 2) AS avg_order_value,
    ROUND(total_revenue / NULLIF(unique_customers, 0), 2) AS revenue_per_customer
FROM country_metrics
ORDER BY total_revenue DESC;


-- UK vs International comparison
SELECT
    CASE WHEN Country = 'United Kingdom' THEN 'UK' ELSE 'International' END AS region,
    COUNT(DISTINCT CustomerID) AS customers,
    COUNT(DISTINCT InvoiceNo) AS orders,
    ROUND(SUM(TotalAmount), 2) AS revenue,
    ROUND(SUM(TotalAmount) * 100.0 / (SELECT SUM(TotalAmount) FROM data_final), 1) AS pct_of_total,
    ROUND(AVG(TotalAmount), 2) AS avg_transaction_value
FROM data_final
GROUP BY CASE WHEN Country = 'United Kingdom' THEN 'UK' ELSE 'International' END;


-- ============================================================================
-- 5. TIME SERIES ANALYSIS
-- ============================================================================

-- Monthly sales trend with MoM growth (proper date ordering)
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', InvoiceDate) AS month,
        SUM(TotalAmount) AS revenue,
        COUNT(DISTINCT CustomerID) AS active_customers,
        COUNT(DISTINCT InvoiceNo) AS order_count
    FROM data_final
    GROUP BY DATE_TRUNC('month', InvoiceDate)
),
with_growth AS (
    SELECT
        month,
        revenue,
        active_customers,
        order_count,
        LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
        ROUND(
            (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 /
            NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
            1
        ) AS mom_growth_pct
    FROM monthly_sales
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    active_customers,
    order_count,
    ROUND(prev_month_revenue, 2) AS prev_month_revenue,
    mom_growth_pct
FROM with_growth
ORDER BY month;  -- Proper chronological ordering


-- Day of week analysis (with proper ordering)
WITH dow_sales AS (
    SELECT
        DayOfWeek,
        CASE DayOfWeek
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END AS day_order,
        SUM(TotalAmount) AS revenue,
        COUNT(DISTINCT InvoiceNo) AS orders
    FROM data_final
    GROUP BY DayOfWeek
)
SELECT
    DayOfWeek,
    ROUND(revenue, 2) AS revenue,
    orders,
    ROUND(revenue * 100.0 / SUM(revenue) OVER (), 1) AS pct_of_weekly_revenue,
    CASE WHEN DayOfWeek IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type
FROM dow_sales
ORDER BY day_order;


-- Weekend vs Weekday comparison
SELECT
    CASE WHEN DayOfWeek IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(SUM(TotalAmount), 2) AS total_revenue,
    COUNT(DISTINCT InvoiceNo) AS total_orders,
    ROUND(AVG(TotalAmount), 2) AS avg_transaction,
    ROUND(SUM(TotalAmount) * 100.0 / (SELECT SUM(TotalAmount) FROM data_final), 1) AS pct_of_total
FROM data_final
GROUP BY CASE WHEN DayOfWeek IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END;


-- ============================================================================
-- 6. CUSTOMER RETENTION ANALYSIS
-- ============================================================================

-- New vs Returning customers
WITH customer_orders AS (
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS order_count,
        SUM(TotalAmount) AS total_spend
    FROM data_final
    GROUP BY CustomerID
),
classified AS (
    SELECT
        *,
        CASE WHEN order_count = 1 THEN 'One-time' ELSE 'Returning' END AS customer_type
    FROM customer_orders
)
SELECT
    customer_type,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
    ROUND(SUM(total_spend), 2) AS total_revenue,
    ROUND(SUM(total_spend) * 100.0 / SUM(SUM(total_spend)) OVER (), 1) AS pct_of_revenue,
    ROUND(AVG(total_spend), 2) AS avg_clv
FROM classified
GROUP BY customer_type;


-- Customer cohort analysis (by first purchase month)
WITH first_purchase AS (
    SELECT
        CustomerID,
        DATE_TRUNC('month', MIN(InvoiceDate)) AS cohort_month
    FROM data_final
    GROUP BY CustomerID
),
cohort_data AS (
    SELECT
        fp.cohort_month,
        d.CustomerID,
        DATE_TRUNC('month', d.InvoiceDate) AS purchase_month,
        d.TotalAmount
    FROM data_final d
    JOIN first_purchase fp ON d.CustomerID = fp.CustomerID
)
SELECT
    cohort_month,
    COUNT(DISTINCT CustomerID) AS cohort_size,
    ROUND(SUM(TotalAmount), 2) AS cohort_revenue,
    ROUND(SUM(TotalAmount) / COUNT(DISTINCT CustomerID), 2) AS revenue_per_customer
FROM cohort_data
GROUP BY cohort_month
ORDER BY cohort_month;


-- ============================================================================
-- 7. PRODUCT BASKET ANALYSIS
-- ============================================================================

-- Products frequently bought together (market basket)
WITH order_products AS (
    SELECT DISTINCT
        InvoiceNo,
        StockCode,
        Description
    FROM data_final
),
product_pairs AS (
    SELECT
        a.StockCode AS product_a,
        a.Description AS desc_a,
        b.StockCode AS product_b,
        b.Description AS desc_b,
        COUNT(DISTINCT a.InvoiceNo) AS times_bought_together
    FROM order_products a
    JOIN order_products b
        ON a.InvoiceNo = b.InvoiceNo
        AND a.StockCode < b.StockCode  -- Avoid duplicates and self-joins
    GROUP BY a.StockCode, a.Description, b.StockCode, b.Description
    HAVING COUNT(DISTINCT a.InvoiceNo) >= 50  -- Minimum threshold
)
SELECT
    product_a,
    desc_a,
    product_b,
    desc_b,
    times_bought_together,
    RANK() OVER (ORDER BY times_bought_together DESC) AS pair_rank
FROM product_pairs
ORDER BY times_bought_together DESC
LIMIT 20;


-- ============================================================================
-- 8. PARETO ANALYSIS (80/20 Rule)
-- ============================================================================

-- Product Pareto analysis
WITH product_revenue AS (
    SELECT
        StockCode,
        Description,
        SUM(TotalAmount) AS revenue
    FROM data_final
    GROUP BY StockCode, Description
),
ranked AS (
    SELECT
        StockCode,
        Description,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER () AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS product_rank,
        COUNT(*) OVER () AS total_products
    FROM product_revenue
)
SELECT
    product_rank,
    StockCode,
    Description,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND(cumulative_revenue * 100.0 / total_revenue, 2) AS cumulative_pct,
    ROUND(product_rank * 100.0 / total_products, 2) AS pct_of_products
FROM ranked
WHERE cumulative_revenue * 100.0 / total_revenue <= 80  -- Products driving 80% of revenue
ORDER BY product_rank;


-- Summary: How many products drive 80% of revenue?
WITH product_revenue AS (
    SELECT
        StockCode,
        SUM(TotalAmount) AS revenue
    FROM data_final
    GROUP BY StockCode
),
ranked AS (
    SELECT
        StockCode,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER () AS total_revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS product_rank,
        COUNT(*) OVER () AS total_products
    FROM product_revenue
)
SELECT
    COUNT(*) AS products_for_80pct,
    (SELECT total_products FROM ranked LIMIT 1) AS total_products,
    ROUND(COUNT(*) * 100.0 / (SELECT total_products FROM ranked LIMIT 1), 1) AS pct_of_products,
    '80%' AS revenue_contribution
FROM ranked
WHERE cumulative_revenue * 100.0 / total_revenue <= 80;


-- ============================================================================
-- 9. PRICE SENSITIVITY ANALYSIS
-- ============================================================================

SELECT
    PriceCategory,
    COUNT(*) AS transactions,
    COUNT(DISTINCT CustomerID) AS unique_customers,
    ROUND(SUM(TotalAmount), 2) AS total_revenue,
    ROUND(AVG(Quantity), 1) AS avg_quantity_per_transaction,
    ROUND(AVG(TotalAmount), 2) AS avg_transaction_value,
    ROUND(SUM(TotalAmount) * 100.0 / (SELECT SUM(TotalAmount) FROM data_final), 1) AS pct_of_revenue
FROM data_final
GROUP BY PriceCategory
ORDER BY
    CASE PriceCategory
        WHEN 'Low' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'High' THEN 3
    END;


-- ============================================================================
-- 10. BUSINESS KPI DASHBOARD QUERY
-- ============================================================================

-- Executive summary metrics
SELECT
    'Total Revenue' AS metric,
    ROUND(SUM(TotalAmount), 2) AS value
FROM data_final

UNION ALL

SELECT
    'Total Orders',
    COUNT(DISTINCT InvoiceNo)
FROM data_final

UNION ALL

SELECT
    'Total Customers',
    COUNT(DISTINCT CustomerID)
FROM data_final

UNION ALL

SELECT
    'Avg Order Value',
    ROUND(SUM(TotalAmount) / COUNT(DISTINCT InvoiceNo), 2)
FROM data_final

UNION ALL

SELECT
    'Avg Customer LTV',
    ROUND(SUM(TotalAmount) / COUNT(DISTINCT CustomerID), 2)
FROM data_final

UNION ALL

SELECT
    'Products Sold',
    COUNT(DISTINCT StockCode)
FROM data_final

UNION ALL

SELECT
    'Countries Served',
    COUNT(DISTINCT Country)
FROM data_final;
