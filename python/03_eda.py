"""
=============================================================
  E-Commerce Sales & Customer Analytics
  Phase 3 — Exploratory Data Analysis (EDA)
=============================================================
  Generates professional charts saved as PNG files in
  the visualizations/ folder
=============================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive backend (saves to file)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR  = os.path.join(BASE_DIR, "..", "data", "cleaned")
VIZ_DIR    = os.path.join(BASE_DIR, "..", "visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

# ── Global style ──────────────────────────────────────────────
PALETTE    = ["#4361EE", "#F72585", "#4CC9F0", "#7209B7", "#3A0CA3",
              "#560BAD", "#480CA8", "#3F37C9"]
BG_COLOR   = "#0F0F1A"
TEXT_COLOR = "#E0E0E0"
GRID_COLOR = "#2A2A3E"
ACCENT     = "#4361EE"

def set_dark_style():
    plt.rcParams.update({
        "figure.facecolor"  : BG_COLOR,
        "axes.facecolor"    : "#16162A",
        "axes.edgecolor"    : GRID_COLOR,
        "axes.labelcolor"   : TEXT_COLOR,
        "axes.titlecolor"   : TEXT_COLOR,
        "axes.titlesize"    : 14,
        "axes.labelsize"    : 11,
        "xtick.color"       : TEXT_COLOR,
        "ytick.color"       : TEXT_COLOR,
        "text.color"        : TEXT_COLOR,
        "grid.color"        : GRID_COLOR,
        "grid.linestyle"    : "--",
        "grid.alpha"        : 0.5,
        "legend.facecolor"  : "#16162A",
        "legend.edgecolor"  : GRID_COLOR,
        "font.family"       : "DejaVu Sans",
        "figure.dpi"        : 150,
    })

set_dark_style()

def save(fig, name):
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"  Saved: visualizations/{name}")

def fmt_inr(x, _):
    """Format axis labels as ₹ crore or lakh."""
    if x >= 1e7:
        return f"₹{x/1e7:.1f}Cr"
    elif x >= 1e5:
        return f"₹{x/1e5:.0f}L"
    return f"₹{x:,.0f}"

print("=" * 60)
print("  Phase 3 — Exploratory Data Analysis (EDA)")
print("=" * 60)

# ── Load data ─────────────────────────────────────────────────
print("\nLoading cleaned data...")
flat    = pd.read_csv(os.path.join(CLEAN_DIR, "flat_sales.csv"), parse_dates=["order_date"])
cstats  = pd.read_csv(os.path.join(CLEAN_DIR, "customer_stats.csv"))
products= pd.read_csv(os.path.join(CLEAN_DIR, "products_clean.csv"))

print(f"  flat_sales    : {flat.shape}")
print(f"  customer_stats: {cstats.shape}")
print(f"  products      : {products.shape}")


# ══════════════════════════════════════════════════════════════
#  CHART 1 — Monthly Revenue & Profit Trend (Line Chart)
# ══════════════════════════════════════════════════════════════
print("\n[Chart 1] Monthly Revenue & Profit Trend...")

monthly = (
    flat.groupby(["order_year", "order_month"])
    .agg(revenue=("revenue","sum"), profit=("profit","sum"))
    .reset_index()
)
monthly["period"] = pd.to_datetime(
    monthly["order_year"].astype(str) + "-" + monthly["order_month"].astype(str).str.zfill(2)
)
monthly = monthly.sort_values("period")

fig, ax = plt.subplots(figsize=(14, 5))
ax.fill_between(monthly["period"], monthly["revenue"], alpha=0.15, color="#4361EE")
ax.plot(monthly["period"], monthly["revenue"], color="#4361EE", lw=2.5, marker="o",
        markersize=4, label="Revenue")
ax.fill_between(monthly["period"], monthly["profit"], alpha=0.15, color="#F72585")
ax.plot(monthly["period"], monthly["profit"], color="#F72585", lw=2.5, marker="o",
        markersize=4, label="Profit")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title("Monthly Revenue & Profit Trend (2022–2024)", pad=15, fontsize=15, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Amount (INR)")
ax.legend(fontsize=11)
ax.grid(True, axis="y")
fig.tight_layout()
save(fig, "01_monthly_revenue_profit.png")


# ══════════════════════════════════════════════════════════════
#  CHART 2 — Revenue by Category (Horizontal Bar)
# ══════════════════════════════════════════════════════════════
print("[Chart 2] Revenue by Category...")

cat_rev = (
    flat.groupby("category")["revenue"]
    .sum().sort_values(ascending=True)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_rev["category"], cat_rev["revenue"],
               color=PALETTE[:len(cat_rev)], edgecolor="none", height=0.6)
for bar, val in zip(bars, cat_rev["revenue"]):
    ax.text(bar.get_width() + cat_rev["revenue"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            fmt_inr(val, None), va="center", fontsize=9, color=TEXT_COLOR)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title("Total Revenue by Product Category", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Revenue (INR)")
ax.grid(True, axis="x", alpha=0.4)
ax.set_xlim(0, cat_rev["revenue"].max() * 1.2)
fig.tight_layout()
save(fig, "02_revenue_by_category.png")


# ══════════════════════════════════════════════════════════════
#  CHART 3 — Profit Margin by Category (Bar)
# ══════════════════════════════════════════════════════════════
print("[Chart 3] Profit Margin by Category...")

cat_margin = (
    flat.groupby("category")
    .agg(revenue=("revenue","sum"), profit=("profit","sum"))
    .assign(margin=lambda d: (d["profit"]/d["revenue"]*100).round(2))
    .sort_values("margin", ascending=True)
    .reset_index()
)

colors = ["#F72585" if m < 25 else "#4361EE" for m in cat_margin["margin"]]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_margin["category"], cat_margin["margin"],
               color=colors, edgecolor="none", height=0.6)
for bar, val in zip(bars, cat_margin["margin"]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=9, color=TEXT_COLOR)
ax.axvline(25, color="#FFD166", lw=1.5, linestyle="--", label="25% threshold")
ax.set_title("Profit Margin % by Category", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Profit Margin (%)")
ax.grid(True, axis="x", alpha=0.4)
ax.legend(fontsize=10)
ax.set_xlim(0, cat_margin["margin"].max() * 1.25)
fig.tight_layout()
save(fig, "03_profit_margin_by_category.png")


# ══════════════════════════════════════════════════════════════
#  CHART 4 — Top 10 Products by Revenue (Bar)
# ══════════════════════════════════════════════════════════════
print("[Chart 4] Top 10 Products by Revenue...")

top10 = (
    flat.groupby("product_name")["revenue"]
    .sum().nlargest(10).sort_values(ascending=True)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(top10["product_name"], top10["revenue"],
               color=ACCENT, edgecolor="none", height=0.6,
               linewidth=0)
# Gradient effect
for i, bar in enumerate(bars):
    bar.set_alpha(0.6 + 0.04 * i)
for bar, val in zip(bars, top10["revenue"]):
    ax.text(bar.get_width() + top10["revenue"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            fmt_inr(val, None), va="center", fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title("Top 10 Products by Revenue", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Revenue (INR)")
ax.grid(True, axis="x", alpha=0.4)
ax.set_xlim(0, top10["revenue"].max() * 1.22)
fig.tight_layout()
save(fig, "04_top10_products.png")


# ══════════════════════════════════════════════════════════════
#  CHART 5 — Revenue by Region (Donut / Pie)
# ══════════════════════════════════════════════════════════════
print("[Chart 5] Revenue by Region...")

reg_rev = flat.groupby("region")["revenue"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    reg_rev.values,
    labels=reg_rev.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=PALETTE[:len(reg_rev)],
    pctdistance=0.78,
    wedgeprops=dict(width=0.5, edgecolor=BG_COLOR, linewidth=2)
)
for t in texts:
    t.set_color(TEXT_COLOR); t.set_fontsize(11)
for at in autotexts:
    at.set_color("white"); at.set_fontsize(9); at.set_fontweight("bold")
ax.set_title("Revenue Distribution by Region", fontsize=15, fontweight="bold", pad=15)
fig.tight_layout()
save(fig, "05_revenue_by_region.png")


# ══════════════════════════════════════════════════════════════
#  CHART 6 — Monthly Revenue by Year (Grouped Lines)
# ══════════════════════════════════════════════════════════════
print("[Chart 6] Monthly Revenue by Year (YoY comparison)...")

yoy = flat.groupby(["order_year", "order_month"])["revenue"].sum().reset_index()
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
YEAR_COLORS  = {"2022": "#4CC9F0", "2023": "#4361EE", "2024": "#F72585"}

fig, ax = plt.subplots(figsize=(13, 5))
for year, grp in yoy.groupby("order_year"):
    ax.plot(grp["order_month"], grp["revenue"],
            marker="o", markersize=5, lw=2.5,
            color=YEAR_COLORS.get(str(year), PALETTE[0]),
            label=str(year))
ax.set_xticks(range(1, 13))
ax.set_xticklabels(MONTH_LABELS)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title("Year-over-Year Monthly Revenue Comparison", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (INR)")
ax.legend(title="Year", fontsize=11)
ax.grid(True, alpha=0.4)
fig.tight_layout()
save(fig, "06_yoy_monthly_revenue.png")


# ══════════════════════════════════════════════════════════════
#  CHART 7 — Customer Spending Distribution (Histogram)
# ══════════════════════════════════════════════════════════════
print("[Chart 7] Customer Spending Distribution...")

fig, ax = plt.subplots(figsize=(11, 5))
ax.hist(cstats["total_revenue"], bins=60,
        color=ACCENT, edgecolor="none", alpha=0.85)
median_val = cstats["total_revenue"].median()
mean_val   = cstats["total_revenue"].mean()
ax.axvline(median_val, color="#FFD166", lw=2, linestyle="--",
           label=f"Median ₹{median_val:,.0f}")
ax.axvline(mean_val, color="#F72585", lw=2, linestyle="--",
           label=f"Mean ₹{mean_val:,.0f}")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title("Customer Lifetime Spending Distribution", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Total Lifetime Revenue (INR)")
ax.set_ylabel("Number of Customers")
ax.legend(fontsize=11)
ax.grid(True, axis="y", alpha=0.4)
fig.tight_layout()
save(fig, "07_customer_spending_distribution.png")


# ══════════════════════════════════════════════════════════════
#  CHART 8 — Repeat vs New Customer Revenue (Grouped Bar)
# ══════════════════════════════════════════════════════════════
print("[Chart 8] Repeat vs New Customer Revenue...")

repeat_rev = (
    flat.merge(cstats[["customer_id","is_repeat_customer"]], on="customer_id", how="left")
    .groupby("is_repeat_customer")
    .agg(total_revenue=("revenue","sum"),
         avg_order_value=("revenue","mean"),
         customer_count=("customer_id","nunique"))
    .reset_index()
)
repeat_rev["label"] = repeat_rev["is_repeat_customer"].map({True:"Repeat Customers", False:"New Customers"})

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
metrics  = ["total_revenue", "avg_order_value", "customer_count"]
titles   = ["Total Revenue", "Avg Order Value", "Customer Count"]
cols     = ["#4361EE", "#F72585"]

for ax, metric, title in zip(axes, metrics, titles):
    bars = ax.bar(repeat_rev["label"], repeat_rev[metric],
                  color=cols, edgecolor="none", width=0.5)
    for bar in bars:
        val = bar.get_height()
        label = fmt_inr(val, None) if metric != "customer_count" else f"{int(val):,}"
        ax.text(bar.get_x() + bar.get_width()/2, val * 1.02,
                label, ha="center", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel("")
    if metric in ["total_revenue","avg_order_value"]:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_ylim(0, repeat_rev[metric].max() * 1.25)
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(True, axis="y", alpha=0.4)

fig.suptitle("Repeat vs New Customers — Revenue Analysis", fontsize=15, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "08_repeat_vs_new_customers.png")


# ══════════════════════════════════════════════════════════════
#  CHART 9 — Order Status Breakdown (Donut)
# ══════════════════════════════════════════════════════════════
print("[Chart 9] Order Status Breakdown...")

orders_clean = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"))
status_counts = orders_clean["status"].value_counts()
STATUS_COLORS = {"Delivered":"#06D6A0", "Shipped":"#4361EE",
                 "Processing":"#FFD166", "Cancelled":"#F72585", "Returned":"#7209B7"}
colors_used = [STATUS_COLORS.get(s, "#888") for s in status_counts.index]

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    status_counts.values,
    labels=status_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=colors_used,
    pctdistance=0.80,
    wedgeprops=dict(width=0.55, edgecolor=BG_COLOR, linewidth=2)
)
for t in texts:   t.set_color(TEXT_COLOR); t.set_fontsize(11)
for at in autotexts: at.set_color("white"); at.set_fontsize(9); at.set_fontweight("bold")
ax.set_title("Order Status Distribution", fontsize=15, fontweight="bold", pad=15)
fig.tight_layout()
save(fig, "09_order_status.png")


# ══════════════════════════════════════════════════════════════
#  CHART 10 — Revenue Heatmap (Month x Year)
# ══════════════════════════════════════════════════════════════
print("[Chart 10] Revenue Heatmap (Month × Year)...")

heat_data = (
    flat.groupby(["order_year","order_month"])["revenue"]
    .sum().unstack("order_month")
)
heat_data.columns = MONTH_LABELS
heat_data.index   = [str(y) for y in heat_data.index]

fig, ax = plt.subplots(figsize=(14, 4))
sns.heatmap(
    heat_data / 1e6,              # in millions
    annot=True, fmt=".1f",
    cmap="Blues",
    linewidths=0.5, linecolor=BG_COLOR,
    ax=ax,
    cbar_kws={"label": "Revenue (₹ Millions)"}
)
ax.set_title("Monthly Revenue Heatmap (₹ Millions)", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Month")
ax.set_ylabel("Year")
fig.tight_layout()
save(fig, "10_revenue_heatmap.png")


print("\n" + "=" * 60)
print("  Phase 3 COMPLETE — 10 charts saved in visualizations/")
print("=" * 60)
