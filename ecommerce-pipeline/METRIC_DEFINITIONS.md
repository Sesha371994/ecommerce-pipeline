# Metric Definitions (Business Logic Contract)

This is the single source of truth for what each metric means.
Without this, two people calculate "Revenue" two different ways
and both think they're right — that's how dashboards lose trust.

---

### 1. **Total Revenue**
`SUM(quantity × unit_price)` for orders where `status = 'Completed'` ONLY.

**Why exclude Cancelled/Pending?** A cancelled order never generated
real money. A pending order might still fall through. Counting them
inflates revenue and misleads stakeholders about actual sales.

### 2. **Order Count**
Count of distinct `order_id` where `status = 'Completed'`.

### 3. **Average Order Value (AOV)**
`Total Revenue / Order Count` (Completed orders only).

### 4. **Cancellation Rate**
`COUNT(status = 'Cancelled') / COUNT(all orders)`
Measures how often orders fail to convert — an early warning metric.

### 5. **Repeat Customer Rate**
`(Customers with 2+ Completed orders) / (Total customers with 1+ Completed order)`

### 6. **Revenue by Category**
`SUM(revenue)` grouped by `category`, Completed orders only.

### 7. **New vs Returning Customer**
A customer is "New" in a given month if their `signup_date` falls
in that same month. Otherwise "Returning."

---

## Edge Cases Handled

| Edge Case | Decision |
|---|---|
| Quantity = 0 or negative | Excluded entirely (invalid, not a real transaction) |
| Missing customer_email | Excluded (can't attribute revenue to anyone) |
| Status = "Unknown" (unparseable) | Excluded from revenue, but counted separately in a "data quality" metric so it's visible, not hidden |
| Duplicate order rows | De-duplicated on exact match before any calculation |
| Order date unparseable | Excluded from date-based trends, flagged in a QA count |

**Why this matters:** any stakeholder can look at this file, agree
with (or challenge) a definition BEFORE looking at the dashboard —
so once numbers are published, nobody argues about what they mean,
only whether the definition itself needs to change.
