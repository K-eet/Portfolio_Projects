-- Use data_final.csv

-- Print first few rows to check column names
SELECT *
FROM data_final
LIMIT 10

-- Find Top-selling products
SELECT StockCode, 
       Description, 
       SUM(TotalAmount) AS ProductSales
FROM data_final
GROUP BY StockCode, Description
ORDER BY ProductSales DESC;

-- Top 10 Customers by Lifetime Value
SELECT CustomerID, 
       CustomerLifetimeValue
FROM data_final
ORDER BY CustomerLifetimeValue DESC
LIMIT 10;

-- Total Sales and Average Order Value by Country
SELECT Country, 
       SUM(TotalAmount) AS TotalSales, 
       AVG(AvgOrderValue) AS AvgOrderValue
FROM data_final
GROUP BY Country
ORDER BY TotalSales DESC;

-- Monthly Sales Trend
SELECT Month, 
       SUM(TotalAmount) AS MonthlySales
FROM data_final
GROUP BY Month
ORDER BY Month ASC;

--  Number of Returning Customers
SELECT COUNT(CustomerID) AS ReturningCustomers
FROM data_final
WHERE IsReturningCustomer = 1;

--  Weekend Sales vs Weekday sales
SELECT IsWeekend, 
       SUM(TotalAmount) AS TotalSales
FROM data_final
GROUP BY IsWeekend;

-- Product popularity and sales by country
SELECT Country, 
       StockCode, 
       Description, 
       SUM(TotalAmount) AS TotalSales
FROM your_table
GROUP BY Country, StockCode, Description
ORDER BY Country, TotalSales DESC;