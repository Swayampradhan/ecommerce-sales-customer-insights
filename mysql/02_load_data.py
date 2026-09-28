"""
=============================================================
  E-Commerce Sales & Customer Analytics
  Phase 5b — Python MySQL Data Loader
=============================================================
  Loads all cleaned CSVs into MySQL ecommerce_analytics DB.
  
  BEFORE RUNNING:
  1. Make sure MySQL Server is running
  2. Run mysql/01_schema.sql in MySQL Workbench first
  3. Update DB_PASSWORD below with your MySQL root password
=============================================================
"""

import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ── DATABASE CONFIG — UPDATE PASSWORD ────────────────────────
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "root",
    "password": "Latsha@#2005",
    "database": "ecommerce_analytics",
    "allow_local_infile": True,
}

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR = os.path.join(BASE_DIR, "..", "data", "cleaned")

print("=" * 60)
print("  Phase 5b — MySQL Data Loader")
print("=" * 60)

# ── Connect ───────────────────────────────────────────────────
try:
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("\n  Connected to MySQL successfully.")
except Error as e:
    print(f"\n  ERROR connecting to MySQL: {e}")
    print("  Make sure MySQL is running and password is correct.")
    exit(1)

# ── Helper: bulk insert a DataFrame ──────────────────────────
def sanitize(val):
    """Convert NaN / NA / inf to None for MySQL."""
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val

def load_table(df, table_name, columns):
    """Insert DataFrame rows into MySQL table in batches."""
    df_subset = df[columns].copy()

    placeholders = ", ".join(["%s"] * len(columns))
    col_names    = ", ".join(columns)
    sql = f"INSERT IGNORE INTO {table_name} ({col_names}) VALUES ({placeholders})"

    # Convert each cell: NaN → None, keep everything else as-is
    rows = [
        tuple(sanitize(v) for v in row)
        for row in df_subset.itertuples(index=False)
    ]
    
    BATCH = 5000
    total = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        cursor.executemany(sql, batch)
        conn.commit()
        total += len(batch)
        print(f"    Inserted {total:,} / {len(rows):,} rows...", end="\r")
    
    print(f"    Done: {total:,} rows into {table_name}      ")

# ── Load tables in dependency order ───────────────────────────

print("\n[1/5] Loading customers...")
customers = pd.read_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"))
customers["signup_date"] = pd.to_datetime(customers["signup_date"]).dt.strftime("%Y-%m-%d")
load_table(customers, "customers",
           ["customer_id","customer_name","email","phone","city","state","region","segment","signup_date"])

print("\n[2/5] Loading products...")
products = pd.read_csv(os.path.join(CLEAN_DIR, "products_clean.csv"))
load_table(products, "products",
           ["product_id","product_name","category","unit_price","unit_cost"])

print("\n[3/5] Loading orders...")
orders = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"))
orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m-%d")
load_table(orders, "orders",
           ["order_id","customer_id","order_date","status"])

print("\n[4/5] Loading order_items...")
oi = pd.read_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"))
load_table(oi, "order_items",
           ["order_item_id","order_id","product_id","quantity"])

print("\n[5/5] Loading rfm_segments...")
rfm = pd.read_csv(os.path.join(CLEAN_DIR, "rfm_segments.csv"))
load_table(rfm, "rfm_segments",
           ["customer_id","recency","frequency","monetary",
            "R_score","F_score","M_score","RFM_score","RFM_total","segment"])

# ── Verify row counts ─────────────────────────────────────────
print("\n[VERIFY] Row counts in MySQL:")
for table in ["customers","products","orders","order_items","rfm_segments"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table:<20}: {count:>8,} rows")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("  Phase 5 COMPLETE — All data loaded into MySQL!")
print("=" * 60)
