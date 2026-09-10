-- ============================================================
-- STEP 2b: VALIDATION QUERIES
-- Purpose: Before cleaning anything, MEASURE the problems.
-- This is a core habit in analytics: never clean blind, always
-- quantify the mess first so you know what you fixed (and can
-- prove it to stakeholders later).
-- ============================================================

-- 1. Duplicate order rows (same order_id appearing more than once)
SELECT order_id, COUNT(*) as dupe_count
FROM raw_orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 2. Rows with missing/null critical fields
SELECT
  SUM(CASE WHEN customer_email IS NULL THEN 1 ELSE 0 END) AS missing_email,
  SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END)       AS missing_qty,
  SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END)         AS missing_status
FROM raw_orders;

-- 3. Invalid quantities (negative or zero — can't sell -1 items)
SELECT COUNT(*) AS bad_quantity_rows
FROM raw_orders
WHERE quantity <= 0;

-- 4. Status field inconsistency (casing chaos)
SELECT DISTINCT status FROM raw_orders;
-- Expect to see: Completed, completed, COMPLETED, Cancelled, cancelled, Pending, pending, NULL
-- All of these mean only 3 real statuses -> needs standardizing

-- 5. Price field stored as text with currency symbol
SELECT order_id, unit_price
FROM raw_orders
WHERE unit_price LIKE '%₹%';

-- 6. Duplicate customers (same email, different casing)
SELECT LOWER(TRIM(email)) AS normalized_email, COUNT(*) AS variants
FROM raw_customers
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*) > 1;

-- 7. Category casing inconsistency in products
SELECT DISTINCT category FROM raw_products;

-- 8. Orders referencing a customer_email that doesn't exist in customers table
-- (orphan records — common integrity issue)
SELECT o.order_id, o.customer_email
FROM raw_orders o
LEFT JOIN raw_customers c
  ON LOWER(TRIM(o.customer_email)) = LOWER(TRIM(c.email))
WHERE o.customer_email IS NOT NULL
  AND c.email IS NULL;
