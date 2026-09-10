"""
STEP 5: METRICS CALCULATION
Implements the exact definitions from METRIC_DEFINITIONS.md.
Each metric here should be traceable back to that document —
that traceability IS what makes a metric "trustworthy."
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")
fact = pd.read_sql("SELECT * FROM fact_orders", conn)
fact["order_date"] = pd.to_datetime(fact["order_date"])

completed = fact[fact["status"] == "Completed"]

# 1. Total Revenue
total_revenue = completed["revenue"].sum()

# 2. Order Count
order_count = completed["order_id"].nunique()

# 3. AOV
aov = total_revenue / order_count if order_count else 0

# 4. Cancellation Rate
cancel_rate = (fact["status"] == "Cancelled").sum() / len(fact)

# 5. Repeat Customer Rate
orders_per_customer = completed.groupby("customer_email")["order_id"].nunique()
repeat_customers = (orders_per_customer >= 2).sum()
total_customers_with_order = (orders_per_customer >= 1).sum()
repeat_rate = repeat_customers / total_customers_with_order if total_customers_with_order else 0

# 6. Revenue by Category
revenue_by_category = (
    completed.groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .round(2)
)

# 7. Data Quality visibility (Unknown status count — not hidden, reported)
unknown_status_count = (fact["status"] == "Unknown").sum()

# ------------------------------------------------------------
# Monthly revenue trend (for the dashboard line chart)
# ------------------------------------------------------------
completed_copy = completed.copy()
completed_copy["month"] = completed_copy["order_date"].dt.to_period("M").astype(str)
monthly_revenue = completed_copy.groupby("month")["revenue"].sum().round(2)

# ------------------------------------------------------------
# PRINT SUMMARY
# ------------------------------------------------------------
print("=" * 50)
print("METRICS SUMMARY")
print("=" * 50)
print(f"Total Revenue:          ₹{total_revenue:,.2f}")
print(f"Completed Orders:       {order_count}")
print(f"Average Order Value:    ₹{aov:,.2f}")
print(f"Cancellation Rate:      {cancel_rate:.1%}")
print(f"Repeat Customer Rate:   {repeat_rate:.1%}")
print(f"Unknown Status Orders:  {unknown_status_count} (flagged, not hidden)")
print("\nRevenue by Category:")
print(revenue_by_category.to_string())
print("\nMonthly Revenue Trend:")
print(monthly_revenue.to_string())

# ------------------------------------------------------------
# Save a metrics summary table for Excel/Power BI to consume
# ------------------------------------------------------------
summary_df = pd.DataFrame([{
    "total_revenue": round(total_revenue, 2),
    "completed_orders": order_count,
    "aov": round(aov, 2),
    "cancellation_rate_pct": round(cancel_rate * 100, 2),
    "repeat_customer_rate_pct": round(repeat_rate * 100, 2),
    "unknown_status_orders": unknown_status_count,
}])

summary_df.to_csv("exports/metrics_summary.csv", index=False)
revenue_by_category.to_csv("exports/revenue_by_category.csv")
monthly_revenue.to_csv("exports/monthly_revenue.csv")

print("\nSaved: exports/metrics_summary.csv, revenue_by_category.csv, monthly_revenue.csv")

conn.close()
