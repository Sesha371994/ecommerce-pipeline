"""
STEP 6: EXCEL REPORT
Purpose: Turn the clean data into a business-facing report.
Rule (per skill guidance): KPIs use live formulas (SUMIFS/COUNTIFS/
AVERAGEIFS), never hardcoded numbers — so the report recalculates
if the underlying data changes.
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter

fact = pd.read_csv("exports/fact_orders_clean.csv")
fact["order_date"] = pd.to_datetime(fact["order_date"])
fact["month"] = fact["order_date"].dt.strftime("%Y-%m")

wb = Workbook()

FONT = "Arial"
HEADER_FILL = PatternFill(start_color="2A5298", end_color="2A5298", fill_type="solid")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name=FONT, bold=True, size=14, color="1E3C72")
LABEL_FONT = Font(name=FONT, bold=True, size=11)
NORMAL_FONT = Font(name=FONT, size=10)

# ================================================================
# SHEET 1: Raw_Data (pivot-ready — this is what Power BI/Excel
# pivot tables connect to)
# ================================================================
ws_data = wb.active
ws_data.title = "Raw_Data"

cols = ["order_id", "customer_email", "name", "city", "product_id",
        "product_name", "category", "quantity", "unit_price", "revenue",
        "status", "order_date", "month"]

for c_idx, col in enumerate(cols, start=1):
    cell = ws_data.cell(row=1, column=c_idx, value=col.replace("_", " ").title())
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in enumerate(fact[cols].itertuples(index=False), start=2):
    for c_idx, val in enumerate(row, start=1):
        cell = ws_data.cell(row=r_idx, column=c_idx, value=val)
        cell.font = NORMAL_FONT
        if cols[c_idx - 1] == "order_date":
            cell.number_format = "yyyy-mm-dd"
        if cols[c_idx - 1] in ("unit_price", "revenue"):
            cell.number_format = "#,##0.00"

for c_idx, col in enumerate(cols, start=1):
    ws_data.column_dimensions[get_column_letter(c_idx)].width = max(14, len(col) + 4)

n_rows = len(fact) + 1  # +1 header
ws_data.freeze_panes = "A2"

# ================================================================
# SHEET 2: Metrics_Dashboard (formula-driven KPIs + charts)
# ================================================================
ws_dash = wb.create_sheet("Metrics_Dashboard")
ws_dash["B2"] = "E-Commerce Metrics Dashboard"
ws_dash["B2"].font = TITLE_FONT
ws_dash["B3"] = "All figures reflect Completed orders only (see Metric_Definitions sheet)"
ws_dash["B3"].font = Font(name=FONT, italic=True, size=9, color="666666")

status_col = cols.index("status") + 1     # column letter for Status
qty_col = cols.index("quantity") + 1
price_col = cols.index("unit_price") + 1
rev_col = cols.index("revenue") + 1
order_id_col = cols.index("order_id") + 1
cat_col = cols.index("category") + 1
email_col = cols.index("customer_email") + 1

status_letter = get_column_letter(status_col)
rev_letter = get_column_letter(rev_col)
order_id_letter = get_column_letter(order_id_col)
cat_letter = get_column_letter(cat_col)

data_range_status = f"Raw_Data!${status_letter}$2:${status_letter}${n_rows}"
data_range_rev = f"Raw_Data!${rev_letter}$2:${rev_letter}${n_rows}"
data_range_orderid = f"Raw_Data!${order_id_letter}$2:${order_id_letter}${n_rows}"
data_range_cat = f"Raw_Data!${cat_letter}$2:${cat_letter}${n_rows}"

# --- KPI cards (row 6) ---
kpi_labels = ["Total Revenue", "Completed Orders", "Avg Order Value", "Cancellation Rate"]
kpi_cells = ["B6", "D6", "F6", "H6"]

for label, cell_ref in zip(kpi_labels, kpi_cells):
    col_letter = cell_ref[0]
    row = int(cell_ref[1:])
    ws_dash[f"{col_letter}{row}"] = label
    ws_dash[f"{col_letter}{row}"].font = LABEL_FONT

ws_dash["B7"] = f'=SUMIFS({data_range_rev},{data_range_status},"Completed")'
ws_dash["B7"].number_format = '"₹"#,##0.00'
ws_dash["B7"].font = Font(name=FONT, size=16, bold=True, color="2A5298")

ws_dash["D7"] = f'=COUNTIFS({data_range_status},"Completed")'
ws_dash["D7"].font = Font(name=FONT, size=16, bold=True, color="2A5298")

ws_dash["F7"] = f'=IFERROR(B7/D7,0)'
ws_dash["F7"].number_format = '"₹"#,##0.00'
ws_dash["F7"].font = Font(name=FONT, size=16, bold=True, color="2A5298")

ws_dash["H7"] = f'=COUNTIFS({data_range_status},"Cancelled")/COUNTA({data_range_status})'
ws_dash["H7"].number_format = "0.0%"
ws_dash["H7"].font = Font(name=FONT, size=16, bold=True, color="2A5298")

# --- Revenue by Category table (for bar chart) ---
ws_dash["B10"] = "Revenue by Category"
ws_dash["B10"].font = LABEL_FONT

categories = sorted(fact["category"].dropna().unique().tolist())
ws_dash["B11"] = "Category"
ws_dash["C11"] = "Revenue"
ws_dash["B11"].font = HEADER_FONT
ws_dash["C11"].font = HEADER_FONT
ws_dash["B11"].fill = HEADER_FILL
ws_dash["C11"].fill = HEADER_FILL

for i, cat in enumerate(categories, start=12):
    ws_dash[f"B{i}"] = cat
    ws_dash[f"C{i}"] = f'=SUMIFS({data_range_rev},{data_range_status},"Completed",{data_range_cat},B{i})'
    ws_dash[f"C{i}"].number_format = '"₹"#,##0'

last_cat_row = 11 + len(categories)

# --- Monthly Revenue table (for line chart) ---
month_col = cols.index("month") + 1
month_letter = get_column_letter(month_col)
data_range_month = f"Raw_Data!${month_letter}$2:${month_letter}${n_rows}"

ws_dash["E10"] = "Monthly Revenue Trend"
ws_dash["E10"].font = LABEL_FONT
ws_dash["E11"] = "Month"
ws_dash["F11"] = "Revenue"
ws_dash["E11"].font = HEADER_FONT
ws_dash["F11"].font = HEADER_FONT
ws_dash["E11"].fill = HEADER_FILL
ws_dash["F11"].fill = HEADER_FILL

months = sorted(fact["month"].dropna().unique().tolist())
for i, m in enumerate(months, start=12):
    ws_dash[f"E{i}"] = m
    ws_dash[f"F{i}"] = f'=SUMIFS({data_range_rev},{data_range_status},"Completed",{data_range_month},E{i})'
    ws_dash[f"F{i}"].number_format = '"₹"#,##0'

last_month_row = 11 + len(months)

# --- Charts ---
bar = BarChart()
bar.title = "Revenue by Category"
bar.y_axis.title = "Revenue (₹)"
data_ref = Reference(ws_dash, min_col=3, min_row=11, max_row=last_cat_row)
cats_ref = Reference(ws_dash, min_col=2, min_row=12, max_row=last_cat_row)
bar.add_data(data_ref, titles_from_data=True)
bar.set_categories(cats_ref)
bar.width = 14
bar.height = 8
ws_dash.add_chart(bar, "B18")

line = LineChart()
line.title = "Monthly Revenue Trend"
line.y_axis.title = "Revenue (₹)"
data_ref2 = Reference(ws_dash, min_col=6, min_row=11, max_row=last_month_row)
cats_ref2 = Reference(ws_dash, min_col=5, min_row=12, max_row=last_month_row)
line.add_data(data_ref2, titles_from_data=True)
line.set_categories(cats_ref2)
line.width = 14
line.height = 8
ws_dash.add_chart(line, "F18")

for col, width in [("B", 18), ("C", 14), ("D", 14), ("E", 18), ("F", 14), ("G", 14), ("H", 14)]:
    ws_dash.column_dimensions[col].width = width

# ================================================================
# SHEET 3: Metric_Definitions (business logic, human readable)
# ================================================================
ws_def = wb.create_sheet("Metric_Definitions")
ws_def["B2"] = "Metric Definitions"
ws_def["B2"].font = TITLE_FONT

definitions = [
    ("Total Revenue", "SUM(quantity x unit_price) for Completed orders only"),
    ("Completed Orders", "COUNT of distinct orders where status = Completed"),
    ("Avg Order Value (AOV)", "Total Revenue / Completed Orders"),
    ("Cancellation Rate", "COUNT(Cancelled) / COUNT(all orders)"),
    ("", ""),
    ("Note", "Cancelled and Pending orders are excluded from revenue —"),
    ("", "they never generated real, confirmed sales."),
]
ws_def["B4"] = "Metric"
ws_def["C4"] = "Definition"
ws_def["B4"].font = HEADER_FONT
ws_def["C4"].font = HEADER_FONT
ws_def["B4"].fill = HEADER_FILL
ws_def["C4"].fill = HEADER_FILL

for i, (label, definition) in enumerate(definitions, start=5):
    ws_def[f"B{i}"] = label
    ws_def[f"C{i}"] = definition
    ws_def[f"B{i}"].font = LABEL_FONT
    ws_def[f"C{i}"].font = NORMAL_FONT

ws_def.column_dimensions["B"].width = 24
ws_def.column_dimensions["C"].width = 60

wb.save("exports/Ecommerce_Report.xlsx")
print("Saved: exports/Ecommerce_Report.xlsx")
