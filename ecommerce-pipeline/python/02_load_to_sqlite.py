"""
STEP 2a: Load raw CSVs into SQLite as RAW tables (untouched, exactly
as received). This mirrors how real pipelines work — you NEVER edit
raw source data, you load it as-is, then clean it in a separate layer.
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")

customers = pd.read_csv("raw_data/customers.csv")
products = pd.read_csv("raw_data/products.csv")
orders = pd.read_csv("raw_data/orders.csv")

customers.to_sql("raw_customers", conn, if_exists="replace", index=False)
products.to_sql("raw_products", conn, if_exists="replace", index=False)
orders.to_sql("raw_orders", conn, if_exists="replace", index=False)

print("Loaded raw tables into ecommerce.db:")
print(f"  raw_customers: {len(customers)} rows")
print(f"  raw_products:  {len(products)} rows")
print(f"  raw_orders:    {len(orders)} rows")

conn.close()
