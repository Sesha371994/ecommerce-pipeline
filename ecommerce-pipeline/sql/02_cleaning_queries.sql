-- ============================================================
-- STEP 3: CLEANING QUERIES
-- Purpose: Transform raw tables into trustworthy staging tables.
-- Rule: NEVER overwrite raw tables. Always create new clean
-- tables/views so raw data stays available for audit/re-processing.
-- ============================================================

-- --------------------------------------------------------------
-- 3a. CLEAN CUSTOMERS
-- Fixes: trim whitespace, lowercase email (dedupe key), title-case city
-- --------------------------------------------------------------
DROP TABLE IF EXISTS clean_customers;
CREATE TABLE clean_customers AS
SELECT
  customer_id,
  TRIM(name) AS name,
  LOWER(TRIM(email)) AS email,
  signup_date_raw,          -- kept raw; real date parsing done in Python step (multiple formats)
  CASE
    WHEN city IS NULL THEN 'Unknown'
    ELSE UPPER(SUBSTR(TRIM(city),1,1)) || LOWER(SUBSTR(TRIM(city),2))
  END AS city
FROM (
  SELECT customer_id, name, email, signup_date AS signup_date_raw, city
  FROM raw_customers
);

-- --------------------------------------------------------------
-- 3b. CLEAN PRODUCTS
-- Fixes: standardize category casing (Title Case)
-- --------------------------------------------------------------
DROP TABLE IF EXISTS clean_products;
CREATE TABLE clean_products AS
SELECT
  product_id,
  product_name,
  -- Title-case each word in category (handles "Home & Kitchen" style names)
  (
    SELECT GROUP_CONCAT(
      UPPER(SUBSTR(word,1,1)) || LOWER(SUBSTR(word,2)), ' '
    )
    FROM (
      WITH RECURSIVE split(word, rest) AS (
        SELECT '', LOWER(TRIM(category)) || ' '
        UNION ALL
        SELECT
          SUBSTR(rest, 1, INSTR(rest, ' ') - 1),
          SUBSTR(rest, INSTR(rest, ' ') + 1)
        FROM split WHERE rest <> ''
      )
      SELECT word FROM split WHERE word <> ''
    )
  ) AS category,
  unit_price
FROM raw_products;

-- --------------------------------------------------------------
-- 3c. CLEAN ORDERS  (the important one)
-- Fixes:
--   - Remove exact duplicate rows (same order_id + same everything)
--   - Drop rows with missing customer_email (can't attribute revenue)
--   - Drop invalid quantities (<= 0)
--   - Standardize status to 3 clean values
--   - Strip currency symbol from unit_price and cast to number
-- --------------------------------------------------------------
DROP TABLE IF EXISTS clean_orders;
CREATE TABLE clean_orders AS
SELECT DISTINCT   -- removes exact duplicate rows
  order_id,
  LOWER(TRIM(customer_email)) AS customer_email,
  product_id,
  quantity,
  CAST(REPLACE(unit_price, '₹', '') AS REAL) AS unit_price,
  order_date_raw,   -- multi-format dates parsed properly in Python step
  CASE
    WHEN LOWER(TRIM(status)) = 'completed' THEN 'Completed'
    WHEN LOWER(TRIM(status)) = 'cancelled' THEN 'Cancelled'
    WHEN LOWER(TRIM(status)) = 'pending'   THEN 'Pending'
    ELSE 'Unknown'
  END AS status
FROM (
  SELECT order_id, customer_email, product_id, quantity, unit_price,
         order_date AS order_date_raw, status
  FROM raw_orders
)
WHERE customer_email IS NOT NULL
  AND quantity IS NOT NULL
  AND quantity > 0;

-- --------------------------------------------------------------
-- 3d. VALIDATION: confirm the clean table is actually clean
-- --------------------------------------------------------------
-- Should return ZERO rows if cleaning worked:
SELECT COUNT(*) AS remaining_bad_qty FROM clean_orders WHERE quantity <= 0;
SELECT COUNT(*) AS remaining_nulls FROM clean_orders WHERE customer_email IS NULL;
SELECT DISTINCT status FROM clean_orders;  -- should show only Completed/Cancelled/Pending/Unknown

-- Row count comparison (before -> after)
SELECT
  (SELECT COUNT(*) FROM raw_orders) AS raw_row_count,
  (SELECT COUNT(*) FROM clean_orders) AS clean_row_count;
