-- =============================================================
--  E-Commerce Sales & Customer Analytics
--  Phase 6 — SQL Analysis Queries
-- =============================================================
--  12 queries demonstrating:
--   GROUP BY, JOINs, CASE WHEN, CTEs, Subqueries,
--   Window Functions, Date Functions, LAG(), RANK()
-- =============================================================

USE ecommerce_analytics;

-- ─────────────────────────────────────────────────────────────
--  HELPER VIEW: flat_sales
--  Joins all 4 tables into one reusable view for analysis.
--  Concept: VIEW — a saved SELECT query treated as a virtual table.
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW flat_sales AS
SELECT
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    oi.quantity,
    o.customer_id,
    o.order_date,
    o.status,
    p.product_name,
    p.category,
    p.unit_price,
    p.unit_cost,
    c.customer_name,
    c.region,
    c.state,
    c.segment,
    -- Calculated columns
    (oi.quantity * p.unit_price)                          AS revenue,
    (oi.quantity * p.unit_cost)                           AS cost,
    (oi.quantity * p.unit_price) - (oi.quantity * p.unit_cost) AS profit,
    YEAR(o.order_date)                                    AS order_year,
    MONTH(o.order_date)                                   AS order_month,
    QUARTER(o.order_date)                                 AS order_quarter,
    MONTHNAME(o.order_date)                               AS month_name
FROM order_items  oi
JOIN orders       o  ON oi.order_id    = o.order_id
JOIN products     p  ON oi.product_id  = p.product_id
JOIN customers    c  ON o.customer_id  = c.customer_id
WHERE o.status = 'Delivered';   -- Only count delivered orders


-- =============================================================
--  QUERY 1 — Top 10 Products by Revenue
--  Concepts: GROUP BY, ORDER BY, LIMIT, Aggregate Functions
-- =============================================================
-- Business Question: Which products generate the most revenue?
-- 
-- GROUP BY groups all rows with the same product_name together.
-- SUM() adds up revenue for each group.
-- ORDER BY sorts results descending (highest first).
-- LIMIT 10 shows only the top 10 rows.

SELECT
    product_name,
    category,
    SUM(quantity)                   AS total_units_sold,
    ROUND(SUM(revenue), 0)          AS total_revenue,
    ROUND(SUM(profit), 0)           AS total_profit,
    ROUND(AVG(unit_price), 2)       AS avg_unit_price,
    ROUND(SUM(profit)/SUM(revenue)*100, 1) AS profit_margin_pct
FROM flat_sales
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;


-- =============================================================
--  QUERY 2 — Monthly Revenue & Profit Trend
--  Concepts: DATE Functions (YEAR, MONTH), GROUP BY multiple cols
-- =============================================================
-- Business Question: Which months have the highest/lowest sales?
--
-- YEAR() and MONTH() are MySQL date functions that extract parts
-- of a date. DATE_FORMAT formats a date as a readable string.

SELECT
    YEAR(order_date)                            AS year,
    MONTH(order_date)                           AS month_num,
    DATE_FORMAT(order_date, '%b %Y')            AS month_label,
    COUNT(DISTINCT order_id)                    AS total_orders,
    ROUND(SUM(revenue), 0)                      AS monthly_revenue,
    ROUND(SUM(profit), 0)                       AS monthly_profit,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)      AS profit_margin_pct,
    ROUND(SUM(revenue)/COUNT(DISTINCT order_id),0) AS avg_order_value
FROM flat_sales
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY year, month_num;


-- =============================================================
--  QUERY 3 — Revenue & Profit by Category
--  Concepts: GROUP BY, CASE WHEN, Conditional logic
-- =============================================================
-- Business Question: Which categories are most profitable?
--
-- CASE WHEN is SQL's if-else. Here we label margins as
-- High/Medium/Low based on the calculated percentage.

SELECT
    category,
    COUNT(DISTINCT order_id)                    AS total_orders,
    SUM(quantity)                               AS units_sold,
    ROUND(SUM(revenue), 0)                      AS total_revenue,
    ROUND(SUM(profit), 0)                       AS total_profit,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)      AS margin_pct,
    CASE
        WHEN SUM(profit)/SUM(revenue) >= 0.40 THEN 'High Margin'
        WHEN SUM(profit)/SUM(revenue) >= 0.25 THEN 'Medium Margin'
        ELSE 'Low Margin'
    END                                         AS margin_category
FROM flat_sales
GROUP BY category
ORDER BY total_revenue DESC;


-- =============================================================
--  QUERY 4 — Regional Sales Performance
--  Concepts: JOIN + GROUP BY, multiple aggregates
-- =============================================================
-- Business Question: Which regions perform best?

SELECT
    region,
    COUNT(DISTINCT customer_id)                 AS unique_customers,
    COUNT(DISTINCT order_id)                    AS total_orders,
    ROUND(SUM(revenue), 0)                      AS total_revenue,
    ROUND(SUM(profit), 0)                       AS total_profit,
    ROUND(SUM(revenue)/COUNT(DISTINCT customer_id), 0) AS revenue_per_customer,
    ROUND(SUM(revenue)/COUNT(DISTINCT order_id), 0)    AS avg_order_value
FROM flat_sales
GROUP BY region
ORDER BY total_revenue DESC;


-- =============================================================
--  QUERY 5 — Customer Lifetime Value (Top 20 Customers)
--  Concepts: Subquery, DATEDIFF, calculated fields
-- =============================================================
-- Business Question: Who are the most valuable customers?
--
-- A subquery is a SELECT inside another SELECT.
-- The inner query calculates each customer's stats,
-- the outer query filters/sorts them.

SELECT
    customer_id,
    customer_name,
    region,
    total_orders,
    total_units,
    ROUND(total_revenue, 0)         AS lifetime_revenue,
    ROUND(total_profit, 0)          AS lifetime_profit,
    ROUND(avg_order_value, 0)       AS avg_order_value,
    first_purchase,
    last_purchase,
    DATEDIFF(last_purchase, first_purchase) AS customer_tenure_days
FROM (
    -- Inner subquery: aggregate per customer
    SELECT
        customer_id,
        MAX(customer_name)              AS customer_name,
        MAX(region)                     AS region,
        COUNT(DISTINCT order_id)        AS total_orders,
        SUM(quantity)                   AS total_units,
        SUM(revenue)                    AS total_revenue,
        SUM(profit)                     AS total_profit,
        SUM(revenue)/COUNT(DISTINCT order_id) AS avg_order_value,
        MIN(order_date)                 AS first_purchase,
        MAX(order_date)                 AS last_purchase
    FROM flat_sales
    GROUP BY customer_id
) AS customer_summary
ORDER BY lifetime_revenue DESC
LIMIT 20;


-- =============================================================
--  QUERY 6 — Customer Ranking Using Window Function: RANK()
--  Concepts: Window Functions, RANK() OVER (ORDER BY ...)
-- =============================================================
-- Business Question: Rank all customers by total spend.
--
-- WINDOW FUNCTIONS operate across a set of rows related to
-- the current row WITHOUT collapsing them into one row
-- (unlike GROUP BY which collapses).
--
-- RANK() assigns a rank number. If two customers have the same
-- spend, they get the same rank, and the next rank is skipped.
-- DENSE_RANK() doesn't skip ranks.
-- ROW_NUMBER() gives a unique number regardless of ties.

SELECT
    customer_id,
    customer_name,
    region,
    total_orders,
    ROUND(total_revenue, 0)         AS total_revenue,
    RANK()       OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS dense_rank,
    ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS row_num,
    ROUND(
        total_revenue / SUM(total_revenue) OVER () * 100
    , 2)                            AS revenue_share_pct
FROM (
    SELECT
        customer_id,
        MAX(customer_name) AS customer_name,
        MAX(region)        AS region,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(revenue)       AS total_revenue
    FROM flat_sales
    GROUP BY customer_id
) ranked
ORDER BY revenue_rank
LIMIT 25;


-- =============================================================
--  QUERY 7 — Running Total Revenue by Month (Cumulative Sum)
--  Concepts: Window Function SUM() OVER (ORDER BY ...)
-- =============================================================
-- Business Question: How does cumulative revenue grow over time?
--
-- SUM() OVER (ORDER BY period) computes a RUNNING TOTAL.
-- Each row's value = all previous rows + current row.
-- This is impossible with just GROUP BY.

WITH monthly_rev AS (
    SELECT
        YEAR(order_date)   AS yr,
        MONTH(order_date)  AS mo,
        DATE_FORMAT(order_date, '%b %Y') AS period,
        ROUND(SUM(revenue), 0) AS monthly_revenue
    FROM flat_sales
    GROUP BY YEAR(order_date), MONTH(order_date)
)
SELECT
    period,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY yr, mo) AS cumulative_revenue,
    ROUND(
        SUM(monthly_revenue) OVER (ORDER BY yr, mo) / SUM(monthly_revenue) OVER () * 100
    , 1)                                         AS cumulative_pct
FROM monthly_rev
ORDER BY yr, mo;


-- =============================================================
--  QUERY 8 — Month-over-Month Revenue Growth Using LAG()
--  Concepts: CTE + LAG() window function
-- =============================================================
-- Business Question: Is revenue growing or declining month over month?
--
-- CTE (Common Table Expression) = a temporary named result set.
-- Defined with WITH ... AS (...).
-- Cleaner than nested subqueries.
--
-- LAG(column, 1) accesses the value from the PREVIOUS row.
-- Here, LAG gives us last month's revenue so we can calculate growth%.

WITH monthly AS (
    SELECT
        YEAR(order_date)                AS yr,
        MONTH(order_date)               AS mo,
        DATE_FORMAT(order_date, '%b %Y') AS period,
        ROUND(SUM(revenue), 0)          AS revenue
    FROM flat_sales
    GROUP BY YEAR(order_date), MONTH(order_date)
),
with_lag AS (
    SELECT
        period,
        yr,
        mo,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY yr, mo) AS prev_month_revenue
    FROM monthly
)
SELECT
    period,
    revenue                                     AS current_revenue,
    prev_month_revenue,
    revenue - prev_month_revenue                AS revenue_change,
    ROUND(
        (revenue - prev_month_revenue) / prev_month_revenue * 100
    , 1)                                        AS mom_growth_pct,
    CASE
        WHEN revenue > prev_month_revenue THEN 'Growth'
        WHEN revenue < prev_month_revenue THEN 'Decline'
        ELSE 'Flat'
    END                                         AS trend
FROM with_lag
ORDER BY yr, mo;


-- =============================================================
--  QUERY 9 — Repeat vs New Customer Analysis
--  Concepts: CTE + CASE WHEN + JOIN
-- =============================================================
-- Business Question: Are repeat customers spending more?
--
-- First CTE counts orders per customer.
-- Second CTE labels them repeat/new.
-- Main query aggregates by that label.

WITH order_counts AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS num_orders
    FROM flat_sales
    GROUP BY customer_id
),
customer_type AS (
    SELECT
        customer_id,
        num_orders,
        CASE
            WHEN num_orders > 1 THEN 'Repeat Customer'
            ELSE 'New Customer'
        END AS customer_type
    FROM order_counts
)
SELECT
    ct.customer_type,
    COUNT(DISTINCT fs.customer_id)          AS num_customers,
    COUNT(DISTINCT fs.order_id)             AS total_orders,
    ROUND(SUM(fs.revenue), 0)               AS total_revenue,
    ROUND(AVG(fs.revenue), 0)               AS avg_item_revenue,
    ROUND(SUM(fs.revenue)/COUNT(DISTINCT fs.order_id), 0) AS avg_order_value,
    ROUND(SUM(fs.profit)/SUM(fs.revenue)*100, 1) AS margin_pct
FROM flat_sales fs
JOIN customer_type ct ON fs.customer_id = ct.customer_id
GROUP BY ct.customer_type;


-- =============================================================
--  QUERY 10 — Quarterly Revenue by Region (Pivot-style)
--  Concepts: CASE WHEN pivot, GROUP BY multiple columns
-- =============================================================
-- Business Question: How does each region perform each quarter?

SELECT
    region,
    ROUND(SUM(CASE WHEN order_quarter = 1 THEN revenue ELSE 0 END), 0) AS Q1,
    ROUND(SUM(CASE WHEN order_quarter = 2 THEN revenue ELSE 0 END), 0) AS Q2,
    ROUND(SUM(CASE WHEN order_quarter = 3 THEN revenue ELSE 0 END), 0) AS Q3,
    ROUND(SUM(CASE WHEN order_quarter = 4 THEN revenue ELSE 0 END), 0) AS Q4,
    ROUND(SUM(revenue), 0)                                              AS annual_total
FROM flat_sales
WHERE order_year = 2024
GROUP BY region
ORDER BY annual_total DESC;


-- =============================================================
--  QUERY 11 — Declining Regions (Year-over-Year)
--  Concepts: Multiple CTEs + LAG() for YoY comparison
-- =============================================================
-- Business Question: Which regions are experiencing revenue decline?

WITH yearly_region AS (
    SELECT
        region,
        order_year,
        ROUND(SUM(revenue), 0) AS revenue
    FROM flat_sales
    GROUP BY region, order_year
),
region_yoy AS (
    SELECT
        region,
        order_year,
        revenue,
        LAG(revenue, 1) OVER (PARTITION BY region ORDER BY order_year) AS prev_year_revenue
    FROM yearly_region
)
SELECT
    region,
    order_year,
    revenue,
    prev_year_revenue,
    ROUND((revenue - prev_year_revenue) / prev_year_revenue * 100, 1) AS yoy_growth_pct,
    CASE
        WHEN revenue < prev_year_revenue THEN 'DECLINING'
        WHEN revenue > prev_year_revenue THEN 'GROWING'
        ELSE 'FLAT'
    END AS status
FROM region_yoy
WHERE prev_year_revenue IS NOT NULL
ORDER BY region, order_year;


-- =============================================================
--  QUERY 12 — RFM Segment Revenue Summary (JOIN to rfm_segments)
--  Concepts: JOIN between analytical tables, GROUP BY
-- =============================================================
-- Business Question: Which customer segments drive the most revenue?
-- This is the SQL version of our Python RFM output.

SELECT
    r.segment,
    COUNT(DISTINCT r.customer_id)                   AS customers,
    ROUND(AVG(r.recency), 0)                        AS avg_recency_days,
    ROUND(AVG(r.frequency), 1)                      AS avg_orders,
    ROUND(SUM(fs.revenue), 0)                       AS total_revenue,
    ROUND(AVG(fs.revenue), 0)                       AS avg_item_revenue,
    ROUND(SUM(fs.revenue) / (
        SELECT SUM(revenue) FROM flat_sales
    ) * 100, 1)                                     AS revenue_share_pct
FROM rfm_segments r
JOIN flat_sales fs ON r.customer_id = fs.customer_id
GROUP BY r.segment
ORDER BY total_revenue DESC;


-- =============================================================
--  BONUS QUERY — Executive KPI Summary
-- =============================================================

SELECT
    COUNT(DISTINCT order_id)                        AS total_orders,
    COUNT(DISTINCT customer_id)                     AS total_customers,
    ROUND(SUM(revenue), 0)                          AS total_revenue,
    ROUND(SUM(profit), 0)                           AS total_profit,
    ROUND(SUM(profit)/SUM(revenue)*100, 1)          AS overall_margin_pct,
    ROUND(SUM(revenue)/COUNT(DISTINCT order_id), 0) AS avg_order_value,
    MIN(order_date)                                 AS data_from,
    MAX(order_date)                                 AS data_to
FROM flat_sales;
