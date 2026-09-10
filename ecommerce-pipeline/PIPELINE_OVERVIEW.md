# End-to-End Analytics Pipeline — E-Commerce

## Folder Structure
```
raw_data/          Messy source CSVs (customers, products, orders)
python/
  01_generate_raw_data.py    Creates the messy sample data
  02_load_to_sqlite.py       Loads raw CSVs into SQLite
  03_transform_and_join.py   Date parsing + table joins (Python)
  04_calculate_metrics.py    Computes all defined metrics
  05_build_excel_report.py   Builds the final Excel dashboard
sql/
  01_validation_queries.sql  Measures data quality issues BEFORE cleaning
  02_cleaning_queries.sql    SQL cleaning logic (dedupe, standardize, validate)
exports/
  fact_orders_clean.csv      Analysis-ready joined table
  metrics_summary.csv        Final KPI numbers
  Ecommerce_Report.xlsx      Business-facing Excel dashboard (formulas + charts)
METRIC_DEFINITIONS.md        The business logic contract for every metric
```

## How to Run the Full Pipeline (in order)
```bash
pip install pandas openpyxl

python python/01_generate_raw_data.py     # Step 1: raw messy data
python python/02_load_to_sqlite.py        # Step 2: load into SQLite

# Step 3: run sql/01_validation_queries.sql and sql/02_cleaning_queries.sql
# against ecommerce.db (via any SQLite client, or sqlite3 Python module)

python python/03_transform_and_join.py    # Step 4: Python transform + join
python python/04_calculate_metrics.py     # Step 5: calculate metrics
python python/05_build_excel_report.py    # Step 6: build Excel report
```

## The Pipeline Philosophy (what this teaches)
1. **Never trust raw data** — validate and measure problems first
2. **SQL for set-based cleaning** (dupes, casing, nulls) — it's fast and declarative
3. **Python for messier logic** (multi-format dates, joins, iterative fixes)
4. **Define metrics in writing BEFORE calculating** — this is what "stakeholders can trust" means
5. **Formulas, not hardcoded numbers** in the final report — so it recalculates if data changes
6. **Surface data quality issues, don't hide them** (e.g. "Unknown Status: 37 orders" is shown, not swept away)
