"""
=============================================================
  E-Commerce Sales & Customer Analytics
  Phase 2 — Data Cleaning & Feature Engineering
=============================================================
  Reads raw CSVs → cleans → engineers features → exports
  cleaned CSVs ready for MySQL loading
=============================================================
"""

import os
import pandas as pd
import numpy as np

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
RAW_DIR      = os.path.join(BASE_DIR, "..", "data", "raw")
CLEANED_DIR  = os.path.join(BASE_DIR, "..", "data", "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

print("=" * 60)
print("  Phase 2 — Data Cleaning & Feature Engineering")
print("=" * 60)


# ══════════════════════════════════════════════════════════════
#  STEP 1 — LOAD RAW DATA
# ══════════════════════════════════════════════════════════════
print("\n[STEP 1] Loading raw CSV files...")

customers  = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
products   = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
orders     = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
order_items = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))

print(f"  customers   : {customers.shape}")
print(f"  products    : {products.shape}")
print(f"  orders      : {orders.shape}")
print(f"  order_items : {order_items.shape}")


# ══════════════════════════════════════════════════════════════
#  STEP 2 — INJECT INTENTIONAL DIRTY DATA (for demo purposes)
#            so we actually have something to clean!
# ══════════════════════════════════════════════════════════════
print("\n[STEP 2] Injecting dirty data (nulls, dupes, bad types)...")

np.random.seed(99)

# 2a. Insert ~200 duplicate rows in orders
dup_rows = orders.sample(200, random_state=1)
orders = pd.concat([orders, dup_rows], ignore_index=True)
print(f"  Orders after adding duplicates : {len(orders):,}")

# 2b. Nullify ~1% of customer emails and phone numbers
null_idx = customers.sample(frac=0.01, random_state=2).index
customers.loc[null_idx, "email"] = np.nan
customers.loc[null_idx, "phone"] = np.nan

# 2c. Corrupt some order dates (set to future or nonsense string)
bad_date_idx = orders.sample(50, random_state=3).index
orders.loc[bad_date_idx, "order_date"] = "9999-99-99"

# 2d. Add negative quantities (bad data entry)
bad_qty_idx = order_items.sample(30, random_state=4).index
order_items.loc[bad_qty_idx, "quantity"] = -1

# 2e. Wrong data types — quantity as float with NaN
order_items["quantity"] = order_items["quantity"].astype(float)
order_items.loc[order_items.sample(20, random_state=5).index, "quantity"] = np.nan

print("  Dirty data injected.")


# ══════════════════════════════════════════════════════════════
#  STEP 3 — CLEAN CUSTOMERS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 3] Cleaning customers table...")

before = len(customers)

# 3a. Drop duplicate customer_id rows (keep first occurrence)
customers = customers.drop_duplicates(subset="customer_id", keep="first")

# 3b. Fix missing emails — fill with a placeholder pattern
missing_emails = customers["email"].isna().sum()
customers["email"] = customers["email"].fillna(
    customers["customer_id"].apply(lambda x: f"customer_{x}@unknown.com")
)

# 3c. Fix missing phone — fill with "N/A"
customers["phone"] = customers["phone"].fillna("N/A")

# 3d. Fix data types — signup_date to datetime
customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")

# 3e. Strip whitespace from string columns
for col in ["customer_name", "city", "state", "region", "segment"]:
    customers[col] = customers[col].str.strip()

after = len(customers)
print(f"  Rows before: {before:,} | After dedup: {after:,}")
print(f"  Missing emails fixed : {missing_emails}")
print(f"  signup_date dtype    : {customers['signup_date'].dtype}")


# ══════════════════════════════════════════════════════════════
#  STEP 4 — CLEAN PRODUCTS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 4] Cleaning products table...")

# 4a. Check for nulls
print(f"  Nulls in products:\n{products.isnull().sum().to_string()}")

# 4b. Ensure numeric types
products["unit_price"] = pd.to_numeric(products["unit_price"], errors="coerce")
products["unit_cost"]  = pd.to_numeric(products["unit_cost"],  errors="coerce")

# 4c. Sanity check: cost should never exceed price
invalid_margin = products[products["unit_cost"] >= products["unit_price"]]
print(f"  Products with cost >= price: {len(invalid_margin)}")

print(f"  Products clean. Shape: {products.shape}")


# ══════════════════════════════════════════════════════════════
#  STEP 5 — CLEAN ORDERS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 5] Cleaning orders table...")

before = len(orders)

# 5a. Remove exact duplicate rows
orders = orders.drop_duplicates()
after_dedup = len(orders)
print(f"  Rows before: {before:,} | After dedup: {after_dedup:,} | Removed: {before-after_dedup:,}")

# 5b. Parse order_date — coerce invalid dates to NaT
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

# 5c. Drop rows with null or future order_date
today = pd.Timestamp("2025-01-01")   # reference point
bad_dates = orders["order_date"].isna() | (orders["order_date"] > today)
print(f"  Rows with bad/future dates: {bad_dates.sum()}")
orders = orders[~bad_dates].copy()

# 5d. Make sure order_date is within our expected range
print(f"  Date range: {orders['order_date'].min().date()} → {orders['order_date'].max().date()}")

# 5e. Ensure correct types
orders["order_id"]    = orders["order_id"].astype(int)
orders["customer_id"] = orders["customer_id"].astype(int)

print(f"  Final orders shape: {orders.shape}")


# ══════════════════════════════════════════════════════════════
#  STEP 6 — CLEAN ORDER_ITEMS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 6] Cleaning order_items table...")

before = len(order_items)

# 6a. Drop rows with null quantity
order_items = order_items.dropna(subset=["quantity"])

# 6b. Drop rows with negative or zero quantity
order_items = order_items[order_items["quantity"] > 0]

# 6c. Convert quantity to int
order_items["quantity"] = order_items["quantity"].astype(int)

# 6d. Only keep order_items that belong to valid (cleaned) orders
valid_order_ids = set(orders["order_id"])
order_items = order_items[order_items["order_id"].isin(valid_order_ids)]

after = len(order_items)
print(f"  Rows before: {before:,} | After cleaning: {after:,} | Removed: {before-after:,}")


# ══════════════════════════════════════════════════════════════
#  STEP 7 — FEATURE ENGINEERING (JOIN + CALCULATE)
# ══════════════════════════════════════════════════════════════
print("\n[STEP 7] Feature Engineering...")

# 7a. Build master flat table by joining all 4 tables
#     order_items → join products → join orders → join customers
flat = (
    order_items
    .merge(products[["product_id", "product_name", "category", "unit_price", "unit_cost"]],
           on="product_id", how="left")
    .merge(orders[["order_id", "customer_id", "order_date", "status"]],
           on="order_id", how="left")
    .merge(customers[["customer_id", "customer_name", "region", "state", "segment", "signup_date"]],
           on="customer_id", how="left")
)

print(f"  Flat table shape: {flat.shape}")

# 7b. Derived columns
flat["revenue"]       = flat["quantity"] * flat["unit_price"]
flat["cost"]          = flat["quantity"] * flat["unit_cost"]
flat["profit"]        = flat["revenue"] - flat["cost"]
flat["profit_margin"] = (flat["profit"] / flat["revenue"]).round(4)

# 7c. Time features from order_date
flat["order_date"]    = pd.to_datetime(flat["order_date"])
flat["order_year"]    = flat["order_date"].dt.year
flat["order_month"]   = flat["order_date"].dt.month
flat["order_quarter"] = flat["order_date"].dt.quarter
flat["order_month_name"] = flat["order_date"].dt.strftime("%b")   # Jan, Feb, ...
flat["order_week"]    = flat["order_date"].dt.isocalendar().week.astype(int)
flat["order_dayofweek"] = flat["order_date"].dt.day_name()        # Monday, Tuesday…

# 7d. Only include delivered orders in revenue analysis
#     (Cancelled / Returned orders don't count as real revenue)
flat_revenue = flat[flat["status"] == "Delivered"].copy()
print(f"  Revenue-eligible rows (Delivered): {len(flat_revenue):,}")

# 7e. Customer-level aggregation → CLV + repeat flag
customer_stats = (
    flat_revenue
    .groupby("customer_id")
    .agg(
        total_orders      = ("order_id",  "nunique"),
        total_revenue     = ("revenue",   "sum"),
        total_profit      = ("profit",    "sum"),
        avg_order_value   = ("revenue",   lambda x: x.groupby(
                                flat_revenue.loc[x.index, "order_id"]).sum().mean()),
        first_order_date  = ("order_date","min"),
        last_order_date   = ("order_date","max"),
    )
    .reset_index()
)

# 7f. is_repeat_customer: ordered more than once
customer_stats["is_repeat_customer"] = customer_stats["total_orders"] > 1

# 7g. Customer Lifetime Value (CLV) — simplified as total revenue
customer_stats["clv"] = customer_stats["total_revenue"].round(2)

# 7h. Customer segment based on CLV percentiles
q75 = customer_stats["clv"].quantile(0.75)
q50 = customer_stats["clv"].quantile(0.50)
q25 = customer_stats["clv"].quantile(0.25)

def classify_clv(val):
    if val >= q75:   return "High Value"
    elif val >= q50: return "Mid Value"
    elif val >= q25: return "Low Value"
    else:            return "Churned Risk"

customer_stats["clv_segment"] = customer_stats["clv"].apply(classify_clv)

print(f"  Customer stats shape: {customer_stats.shape}")
print(f"  Repeat customers: {customer_stats['is_repeat_customer'].sum():,} / {len(customer_stats):,}")
print(f"  CLV Segment distribution:\n{customer_stats['clv_segment'].value_counts().to_string()}")


# ══════════════════════════════════════════════════════════════
#  STEP 8 — EXPORT CLEANED DATA
# ══════════════════════════════════════════════════════════════
print("\n[STEP 8] Exporting cleaned data to data/cleaned/...")

customers.to_csv(os.path.join(CLEANED_DIR, "customers_clean.csv"), index=False)
products.to_csv(os.path.join(CLEANED_DIR, "products_clean.csv"), index=False)
orders.to_csv(os.path.join(CLEANED_DIR, "orders_clean.csv"), index=False)
order_items.to_csv(os.path.join(CLEANED_DIR, "order_items_clean.csv"), index=False)
flat_revenue.to_csv(os.path.join(CLEANED_DIR, "flat_sales.csv"), index=False)
customer_stats.to_csv(os.path.join(CLEANED_DIR, "customer_stats.csv"), index=False)

print("  Saved: customers_clean.csv")
print("  Saved: products_clean.csv")
print("  Saved: orders_clean.csv")
print("  Saved: order_items_clean.csv")
print("  Saved: flat_sales.csv  (master joined table)")
print("  Saved: customer_stats.csv")

# ── Final summary ─────────────────────────────────────────────
print("\n[SUMMARY]")
total_revenue = flat_revenue["revenue"].sum()
total_profit  = flat_revenue["profit"].sum()
total_orders  = flat_revenue["order_id"].nunique()
total_cust    = flat_revenue["customer_id"].nunique()
avg_order_val = total_revenue / total_orders

print(f"  Total Revenue  : Rs {total_revenue:,.0f}")
print(f"  Total Profit   : Rs {total_profit:,.0f}")
print(f"  Profit Margin  : {(total_profit/total_revenue)*100:.1f}%")
print(f"  Total Orders   : {total_orders:,}")
print(f"  Total Customers: {total_cust:,}")
print(f"  Avg Order Value: Rs {avg_order_val:,.0f}")

print("\n" + "=" * 60)
print("  Phase 2 COMPLETE — Cleaned data ready in data/cleaned/")
print("=" * 60)
