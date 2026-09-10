"""
STEP 1: Generate messy raw data (simulates a real export from a
messy production database — this is what analysts ACTUALLY get,
never clean data).

Intentional problems planted here (on purpose, for practice):
- Duplicate order rows
- Missing values (nulls) in email, quantity, price
- Inconsistent date formats
- Inconsistent text casing ("Electronics" vs "electronics" vs "ELECTRONICS")
- Negative/zero quantities (data entry errors)
- Whitespace issues in text fields
- Currency symbols mixed into price field (as text)
- Duplicate customer emails with different casing
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# ---------------------------------------------------------
# CUSTOMERS (with intentional dupes / casing issues)
# ---------------------------------------------------------
first_names = ["Arun", "Priya", "Karthik", "Divya", "Ravi", "Sneha", "Vijay",
               "Meena", "Suresh", "Anitha", "Ramesh", "Kavya", "Naveen", "Lakshmi"]
last_names = ["Kumar", "Raj", "Sharma", "Nair", "Iyer", "Reddy", "Pillai", "Das"]

customers = []
for i in range(1, 61):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    email = f"{fname.lower()}.{lname.lower()}{i}@mail.com"
    # randomly mess up casing on some emails (duplicate customer, looks different)
    if random.random() < 0.15:
        email = email.upper()
    signup_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))
    # inconsistent date format
    date_fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"])
    customers.append({
        "customer_id": f"C{i:04d}",
        "name": f"  {fname} {lname}  " if random.random() < 0.1 else f"{fname} {lname}",  # stray whitespace
        "email": email,
        "signup_date": signup_date.strftime(date_fmt),
        "city": random.choice(["Chennai", "chennai", "CHENNAI", "Bangalore", "bangalore",
                                "Mumbai", "Hyderabad", "Coimbatore", None]),
    })

with open("raw_data/customers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)

# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------
categories = ["Electronics", "electronics", "ELECTRONICS", "Fashion", "fashion",
              "Home & Kitchen", "home & kitchen", "Beauty", "Sports"]
product_names = [
    ("Wireless Earbuds", "Electronics", 1499),
    ("Bluetooth Speaker", "Electronics", 2299),
    ("Cotton T-Shirt", "Fashion", 499),
    ("Denim Jeans", "Fashion", 1299),
    ("Non-stick Pan", "Home & Kitchen", 899),
    ("Yoga Mat", "Sports", 699),
    ("Face Serum", "Beauty", 599),
    ("Running Shoes", "Sports", 2499),
    ("Backpack", "Fashion", 1099),
    ("LED Desk Lamp", "Home & Kitchen", 799),
    ("Phone Case", "Electronics", 299),
    ("Sunglasses", "Fashion", 899),
]

products = []
for i, (name, cat, price) in enumerate(product_names, start=1):
    products.append({
        "product_id": f"P{i:03d}",
        "product_name": name,
        "category": random.choice([cat, cat.lower(), cat.upper()]),  # inconsistent casing
        "unit_price": price,
    })

with open("raw_data/products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(products)

# ---------------------------------------------------------
# ORDERS (the messy transactional data)
# ---------------------------------------------------------
orders = []
order_id_counter = 1

for _ in range(450):
    cust = random.choice(customers)
    prod = random.choice(products)
    order_date = datetime(2024, 6, 1) + timedelta(days=random.randint(0, 210))
    date_fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"])

    qty = random.choice([1, 1, 2, 2, 3, 0, -1, None])  # bad values mixed in
    price = prod["unit_price"]

    # sometimes price stored as text with currency symbol
    price_val = f"₹{price}" if random.random() < 0.1 else price

    row = {
        "order_id": f"O{order_id_counter:05d}",
        "customer_email": cust["email"],
        "product_id": prod["product_id"],
        "quantity": qty,
        "unit_price": price_val,
        "order_date": order_date.strftime(date_fmt),
        "status": random.choice(["Completed", "completed", "COMPLETED",
                                  "Cancelled", "cancelled", "Pending", "pending", None]),
    }
    orders.append(row)
    order_id_counter += 1

    # inject duplicate rows (simulates double-submitted orders / export bug)
    if random.random() < 0.06:
        orders.append(row.copy())
        order_id_counter += 0  # duplicate keeps same order_id on purpose (data bug)

# inject a few rows with missing customer_email
for _ in range(10):
    r = random.choice(orders).copy()
    r["customer_email"] = None
    r["order_id"] = f"O{order_id_counter:05d}"
    orders.append(r)
    order_id_counter += 1

with open("raw_data/orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=orders[0].keys())
    writer.writeheader()
    writer.writerows(orders)

print(f"Generated: {len(customers)} customers, {len(products)} products, {len(orders)} order rows")
print("Files saved in raw_data/")
