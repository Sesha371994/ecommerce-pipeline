"""
STEP 4: PYTHON TRANSFORMATION LAYER
Purpose: SQL handled row-level cleaning (dupes, nulls, casing).
Python handles what SQL is bad at: fuzzy/multi-format date parsing,
and building the final joined "analysis-ready" table.

This mirrors a real pipeline: SQL for set-based cleaning,
Python for messier logic, then a single trusted output table.
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")

orders = pd.read_sql("SELECT * FROM clean_orders", conn)
customers = pd.read_sql("SELECT * FROM clean_customers", conn)
products = pd.read_sql("SELECT * FROM clean_products", conn)

# ------------------------------------------------------------
# Parse multi-format dates (this is why we do it in Python, not SQL)
# pandas' to_datetime with format=None + dayfirst guessing handles
# most cases, but mixed formats need per-row fallback logic.
# ------------------------------------------------------------
def parse_flexible_date(date_str):
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y"]
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT  # couldn't parse -> flag as missing, don't guess

orders["order_date"] = orders["order_date_raw"].apply(parse_flexible_date)

unparsed = orders["order_date"].isna().sum()
print(f"Dates that failed to parse: {unparsed} (flagged as NaT, excluded from date-based metrics)")

orders = orders.drop(columns=["order_date_raw"])

# ------------------------------------------------------------
# Same fix for customer signup_date
# ------------------------------------------------------------
def parse_signup_date(date_str):
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

customers["signup_date"] = customers["signup_date_raw"].apply(parse_signup_date)
customers = customers.drop(columns=["signup_date_raw"])

# ------------------------------------------------------------
# Build the final ANALYSIS-READY table (joined, with computed revenue)
# This is the single table Power BI / Excel will connect to.
# ------------------------------------------------------------
fact = orders.merge(customers, left_on="customer_email", right_on="email", how="left", suffixes=("", "_cust"))
fact = fact.merge(products, on="product_id", how="left", suffixes=("", "_prod"))

fact["revenue"] = fact["quantity"] * fact["unit_price"]

# Only Completed orders count as real revenue (Cancelled/Pending shouldn't inflate sales)
fact["is_completed"] = fact["status"] == "Completed"

# ------------------------------------------------------------
# Final integrity check: any orders that failed to join to a customer?
# ------------------------------------------------------------
orphan_orders = fact["name"].isna().sum()
print(f"Orders with no matching customer record: {orphan_orders}")

# Save analysis-ready table back to SQLite + as CSV for Excel/Power BI
fact.to_sql("fact_orders", conn, if_exists="replace", index=False)
fact.to_csv("exports/fact_orders_clean.csv", index=False)

print(f"\nFinal analysis-ready table: {len(fact)} rows")
print(f"Saved to: exports/fact_orders_clean.csv")
print(f"Columns: {list(fact.columns)}")

conn.close()
