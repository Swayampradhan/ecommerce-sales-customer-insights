-- =============================================================
--  E-Commerce Sales & Customer Analytics
--  Phase 5 — MySQL Database Schema
-- =============================================================
--  Run this file in MySQL Workbench FIRST before loading data
-- =============================================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS ecommerce_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ecommerce_analytics;

-- =============================================================
--  TABLE 1: customers
-- =============================================================
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS rfm_segments;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE customers (
    customer_id   INT           NOT NULL,
    customer_name VARCHAR(120)  NOT NULL,
    email         VARCHAR(150),
    phone         VARCHAR(30),
    city          VARCHAR(80),
    state         VARCHAR(80),
    region        VARCHAR(30),
    segment       VARCHAR(30),
    signup_date   DATE,
    PRIMARY KEY (customer_id)
);

-- =============================================================
--  TABLE 2: products
-- =============================================================
CREATE TABLE products (
    product_id    INT            NOT NULL,
    product_name  VARCHAR(120)   NOT NULL,
    category      VARCHAR(60)    NOT NULL,
    unit_price    DECIMAL(10,2)  NOT NULL,
    unit_cost     DECIMAL(10,2)  NOT NULL,
    PRIMARY KEY (product_id)
);

-- =============================================================
--  TABLE 3: orders
-- =============================================================
CREATE TABLE orders (
    order_id      INT          NOT NULL,
    customer_id   INT          NOT NULL,
    order_date    DATE         NOT NULL,
    status        VARCHAR(20)  NOT NULL,
    PRIMARY KEY   (order_id),
    FOREIGN KEY   (customer_id) REFERENCES customers(customer_id)
);

-- =============================================================
--  TABLE 4: order_items
-- =============================================================
CREATE TABLE order_items (
    order_item_id  INT  NOT NULL,
    order_id       INT  NOT NULL,
    product_id     INT  NOT NULL,
    quantity       INT  NOT NULL,
    PRIMARY KEY    (order_item_id),
    FOREIGN KEY    (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY    (product_id) REFERENCES products(product_id)
);

-- =============================================================
--  TABLE 5: rfm_segments  (from Python output)
-- =============================================================
CREATE TABLE rfm_segments (
    customer_id  INT            NOT NULL,
    recency      INT,
    frequency    INT,
    monetary     DECIMAL(14,2),
    R_score      TINYINT,
    F_score      TINYINT,
    M_score      TINYINT,
    RFM_score    VARCHAR(5),
    RFM_total    TINYINT,
    segment      VARCHAR(30),
    PRIMARY KEY  (customer_id),
    FOREIGN KEY  (customer_id) REFERENCES customers(customer_id)
);

-- Verify tables created
SHOW TABLES;

-- =============================================================
--  LOAD DATA (run after schema is created)
--  NOTE: Update file paths to match your system.
--  In MySQL Workbench: Server → Data Import → Import from CSV
--  OR use the Python loader script (recommended).
-- =============================================================

SELECT 'Schema created successfully.' AS status;
