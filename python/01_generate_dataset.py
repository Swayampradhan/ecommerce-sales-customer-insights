"""
=============================================================
  E-Commerce Sales & Customer Analytics
  Phase 1 — Dataset Generator
=============================================================
  Generates a realistic synthetic e-commerce dataset with:
    - 5,000 customers
    - 200 products across 8 categories
    - ~100,000 orders (2022–2024)
    - ~250,000 order line items
  
  Output: data/raw/ folder with 4 CSV files
=============================================================
"""

import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import os

# ── Reproducibility ──────────────────────────────────────────
random.seed(42)
np.random.seed(42)
fake = Faker("en_IN")           # Indian locale → Indian names, cities
Faker.seed(42)

# ── Output path ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(BASE_DIR, "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

print("=" * 60)
print("  E-Commerce Dataset Generator")
print("=" * 60)


# ══════════════════════════════════════════════════════════════
#  TABLE 1 — CUSTOMERS
# ══════════════════════════════════════════════════════════════
print("\n[1/4] Generating customers...")

NUM_CUSTOMERS = 5_000

# Indian regions and their states
REGIONS = {
    "North":  ["Delhi", "Uttar Pradesh", "Haryana", "Punjab", "Rajasthan", "Himachal Pradesh"],
    "South":  ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana"],
    "East":   ["West Bengal", "Bihar", "Odisha", "Jharkhand", "Assam"],
    "West":   ["Maharashtra", "Gujarat", "Goa", "Madhya Pradesh"],
    "Central":["Chhattisgarh", "Uttarakhand", "Jammu & Kashmir"],
}

# Customer segments (for RFM later) — assigned at signup
SEGMENTS_INIT = ["Regular", "Premium", "New", "Occasional"]
SEGMENT_WEIGHTS = [0.45, 0.20, 0.25, 0.10]

def random_region_state():
    region = random.choice(list(REGIONS.keys()))
    state  = random.choice(REGIONS[region])
    return region, state

customers_rows = []
for cid in range(1, NUM_CUSTOMERS + 1):
    region, state = random_region_state()
    signup = fake.date_between(start_date="-4y", end_date="-6m")
    customers_rows.append({
        "customer_id"   : cid,
        "customer_name" : fake.name(),
        "email"         : fake.email(),
        "phone"         : fake.phone_number(),
        "city"          : fake.city(),
        "state"         : state,
        "region"        : region,
        "segment"       : random.choices(SEGMENTS_INIT, SEGMENT_WEIGHTS)[0],
        "signup_date"   : signup,
    })

df_customers = pd.DataFrame(customers_rows)
df_customers.to_csv(os.path.join(RAW_DIR, "customers.csv"), index=False)
print(f"   ✓ {len(df_customers):,} customers saved → data/raw/customers.csv")


# ══════════════════════════════════════════════════════════════
#  TABLE 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════
print("\n[2/4] Generating products...")

# Category → list of (product_name, price_range, margin_range)
PRODUCT_CATALOG = {
    "Electronics": [
        ("Bluetooth Speaker",       (1500, 8000),  (0.12, 0.22)),
        ("Wireless Earbuds",        (800,  5000),  (0.15, 0.25)),
        ("Smartphone",              (8000, 45000), (0.08, 0.15)),
        ("Laptop",                  (35000, 95000),(0.10, 0.18)),
        ("Smart Watch",             (2000, 15000), (0.14, 0.24)),
        ("USB-C Hub",               (600,  2500),  (0.20, 0.35)),
        ("Webcam",                  (1200, 6000),  (0.18, 0.30)),
        ("Mechanical Keyboard",     (1500, 7000),  (0.20, 0.32)),
        ("Gaming Mouse",            (800,  4500),  (0.22, 0.35)),
        ("Portable Charger",        (500,  3000),  (0.25, 0.40)),
    ],
    "Clothing": [
        ("Men's T-Shirt",           (299,  1200),  (0.40, 0.60)),
        ("Women's Kurta",           (499,  2500),  (0.38, 0.58)),
        ("Denim Jeans",             (799,  3500),  (0.35, 0.55)),
        ("Winter Jacket",           (1500, 6000),  (0.30, 0.50)),
        ("Sports Shoes",            (999,  5000),  (0.28, 0.48)),
        ("Saree",                   (799,  8000),  (0.35, 0.55)),
        ("Kids Dress",              (299,  1500),  (0.42, 0.62)),
        ("Formal Shirt",            (599,  2500),  (0.38, 0.55)),
        ("Leggings",                (199,  899),   (0.45, 0.65)),
        ("Ethnic Wear Set",         (1299, 5000),  (0.32, 0.52)),
    ],
    "Home & Kitchen": [
        ("Non-Stick Cookware Set",  (1200, 5000),  (0.30, 0.50)),
        ("Air Fryer",               (2500, 9000),  (0.20, 0.35)),
        ("Mixer Grinder",           (1500, 6000),  (0.22, 0.38)),
        ("Bedsheet Set",            (499,  2500),  (0.38, 0.58)),
        ("Water Purifier",          (5000, 20000), (0.15, 0.28)),
        ("Dinner Set",              (800,  4000),  (0.28, 0.45)),
        ("Vacuum Cleaner",          (3000, 12000), (0.18, 0.32)),
        ("Electric Kettle",         (599,  2500),  (0.30, 0.48)),
        ("Pressure Cooker",         (800,  3500),  (0.28, 0.44)),
        ("Room Freshener Pack",     (199,  899),   (0.45, 0.65)),
    ],
    "Books": [
        ("Data Science Handbook",   (299,  999),   (0.40, 0.60)),
        ("Fiction Novel",           (199,  699),   (0.38, 0.58)),
        ("Self Help Book",          (249,  799),   (0.40, 0.60)),
        ("Engineering Textbook",    (499,  2500),  (0.30, 0.50)),
        ("Children's Story Book",   (149,  499),   (0.42, 0.62)),
        ("Cookbook",                (299,  899),   (0.38, 0.58)),
        ("History Book",            (249,  799),   (0.40, 0.60)),
        ("Business Strategy Book",  (349,  999),   (0.38, 0.58)),
    ],
    "Sports & Fitness": [
        ("Yoga Mat",                (399,  2000),  (0.38, 0.58)),
        ("Dumbbell Set",            (800,  5000),  (0.30, 0.50)),
        ("Resistance Bands",        (299,  1200),  (0.42, 0.62)),
        ("Cricket Bat",             (500,  4000),  (0.28, 0.48)),
        ("Badminton Racket Set",    (400,  3000),  (0.30, 0.50)),
        ("Cycling Helmet",          (500,  3500),  (0.32, 0.52)),
        ("Skipping Rope",           (149,  799),   (0.48, 0.65)),
        ("Gym Gloves",              (299,  1500),  (0.42, 0.60)),
    ],
    "Beauty & Personal Care": [
        ("Face Moisturizer",        (199,  1500),  (0.50, 0.70)),
        ("Hair Serum",              (299,  1200),  (0.48, 0.68)),
        ("Sunscreen SPF50",         (249,  999),   (0.50, 0.70)),
        ("Lipstick Set",            (349,  1500),  (0.52, 0.72)),
        ("Men's Grooming Kit",      (499,  2500),  (0.42, 0.62)),
        ("Perfume",                 (499,  5000),  (0.40, 0.65)),
        ("Shampoo & Conditioner",   (199,  999),   (0.48, 0.68)),
    ],
    "Grocery & Gourmet": [
        ("Organic Honey",           (199,  799),   (0.30, 0.50)),
        ("Dry Fruits Mix",          (399,  1500),  (0.28, 0.48)),
        ("Green Tea Pack",          (199,  699),   (0.35, 0.55)),
        ("Protein Powder",          (999,  3500),  (0.25, 0.45)),
        ("Instant Oats",            (99,   499),   (0.35, 0.55)),
        ("Cold Press Juice",        (149,  599),   (0.28, 0.48)),
    ],
    "Toys & Games": [
        ("LEGO Building Set",       (499,  4000),  (0.30, 0.50)),
        ("Board Game",              (399,  2500),  (0.35, 0.55)),
        ("Remote Control Car",      (799,  4500),  (0.28, 0.48)),
        ("Puzzle Set",              (299,  1500),  (0.38, 0.58)),
        ("Action Figure",           (199,  1200),  (0.40, 0.60)),
        ("Educational Kit",         (499,  2000),  (0.35, 0.55)),
    ],
}

products_rows = []
product_id = 1
for category, items in PRODUCT_CATALOG.items():
    for (name, price_range, margin_range) in items:
        unit_price = round(random.uniform(*price_range), 2)
        margin     = random.uniform(*margin_range)
        unit_cost  = round(unit_price * (1 - margin), 2)
        products_rows.append({
            "product_id"  : product_id,
            "product_name": name,
            "category"    : category,
            "unit_price"  : unit_price,
            "unit_cost"   : unit_cost,
        })
        product_id += 1

df_products = pd.DataFrame(products_rows)
df_products.to_csv(os.path.join(RAW_DIR, "products.csv"), index=False)
print(f"   ✓ {len(df_products):,} products saved → data/raw/products.csv")


# ══════════════════════════════════════════════════════════════
#  TABLE 3 — ORDERS  &  TABLE 4 — ORDER_ITEMS
# ══════════════════════════════════════════════════════════════
print("\n[3/4] Generating orders & order_items (~100K orders)...")

NUM_ORDERS   = 100_000
ORDER_STATUS = ["Delivered", "Delivered", "Delivered", "Delivered",
                "Shipped", "Processing", "Cancelled", "Returned"]

# Some customers are high-frequency buyers (power users)
# We simulate this with a skewed customer selection
customer_ids = df_customers["customer_id"].tolist()
product_ids  = df_products["product_id"].tolist()

# Skew: 20% of customers make 60% of orders (power law)
power_customers  = customer_ids[:1000]           # top 1000 = power users
normal_customers = customer_ids[1000:]

def pick_customer():
    if random.random() < 0.60:
        return random.choice(power_customers)
    return random.choice(normal_customers)

# Date range: Jan 2022 → Dec 2024 (3 full years)
START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)
DATE_RANGE = (END_DATE - START_DATE).days

# Seasonal pattern: Q4 (Oct-Dec) gets 40% more orders, Feb dip
def weighted_date():
    """Generate a date with realistic seasonal distribution."""
    d = START_DATE + timedelta(days=random.randint(0, DATE_RANGE))
    # Festive season boost (Oct-Dec) — Diwali, Christmas, New Year
    if d.month in [10, 11, 12]:
        if random.random() < 0.35:       # extra chance for festive months
            d = START_DATE + timedelta(days=random.randint(
                (datetime(d.year, 10, 1) - START_DATE).days,
                min((datetime(d.year, 12, 31) - START_DATE).days, DATE_RANGE)
            ))
    return d.date()

orders_rows     = []
order_items_rows = []
order_item_id   = 1

for oid in range(1, NUM_ORDERS + 1):
    cid         = pick_customer()
    order_date  = weighted_date()
    status      = random.choice(ORDER_STATUS)

    orders_rows.append({
        "order_id"    : oid,
        "customer_id" : cid,
        "order_date"  : order_date,
        "status"      : status,
    })

    # Each order has 1–5 line items (most orders have 1-2 items)
    num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]

    # Prevent duplicate products in same order
    chosen_products = random.sample(product_ids, min(num_items, len(product_ids)))

    for pid in chosen_products:
        qty = random.choices([1, 2, 3, 4, 5], weights=[55, 25, 12, 5, 3])[0]
        order_items_rows.append({
            "order_item_id": order_item_id,
            "order_id"     : oid,
            "product_id"   : pid,
            "quantity"     : qty,
        })
        order_item_id += 1

df_orders      = pd.DataFrame(orders_rows)
df_order_items = pd.DataFrame(order_items_rows)

df_orders.to_csv(os.path.join(RAW_DIR, "orders.csv"), index=False)
df_order_items.to_csv(os.path.join(RAW_DIR, "order_items.csv"), index=False)

print(f"   ✓ {len(df_orders):,} orders saved → data/raw/orders.csv")
print(f"   ✓ {len(df_order_items):,} order items saved → data/raw/order_items.csv")


# ══════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n[4/4] Dataset summary:")
print(f"   Customers   : {len(df_customers):>8,}")
print(f"   Products    : {len(df_products):>8,}")
print(f"   Orders      : {len(df_orders):>8,}")
print(f"   Order Items : {len(df_order_items):>8,}")

# Quick sanity checks
print("\n   Customer regions:")
print(df_customers["region"].value_counts().to_string())
print("\n   Product categories:")
print(df_products["category"].value_counts().to_string())
print("\n   Order status breakdown:")
print(df_orders["status"].value_counts().to_string())
print("\n   Date range of orders:")
print(f"   From: {df_orders['order_date'].min()}")
print(f"   To  : {df_orders['order_date'].max()}")

print("\n" + "=" * 60)
print("  ✅ Phase 1 COMPLETE — Raw data ready in data/raw/")
print("=" * 60)
