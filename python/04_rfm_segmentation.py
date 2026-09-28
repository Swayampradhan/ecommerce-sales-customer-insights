"""
=============================================================
  E-Commerce Sales & Customer Analytics
  Phase 4 — RFM Customer Segmentation
=============================================================
  RFM = Recency, Frequency, Monetary
  
  Recency  → How many days since last purchase?
  Frequency→ How many orders has the customer placed?
  Monetary → How much total money has the customer spent?
  
  Each dimension is scored 1-5 (5 = best).
  Customers are then classified into 8 business segments.
=============================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR  = os.path.join(BASE_DIR, "..", "data", "cleaned")
VIZ_DIR    = os.path.join(BASE_DIR, "..", "visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────
BG_COLOR   = "#0F0F1A"
TEXT_COLOR = "#E0E0E0"
GRID_COLOR = "#2A2A3E"

plt.rcParams.update({
    "figure.facecolor": BG_COLOR, "axes.facecolor": "#16162A",
    "axes.edgecolor":   GRID_COLOR, "axes.labelcolor":  TEXT_COLOR,
    "axes.titlecolor":  TEXT_COLOR, "xtick.color":      TEXT_COLOR,
    "ytick.color":      TEXT_COLOR, "text.color":       TEXT_COLOR,
    "grid.color":       GRID_COLOR, "grid.linestyle":   "--",
    "grid.alpha":       0.5,        "figure.dpi":       150,
    "font.family":      "DejaVu Sans",
})

print("=" * 60)
print("  Phase 4 — RFM Customer Segmentation")
print("=" * 60)

# ── Load cleaned flat sales ───────────────────────────────────
flat = pd.read_csv(os.path.join(CLEAN_DIR, "flat_sales.csv"), parse_dates=["order_date"])
print(f"\nLoaded flat_sales: {flat.shape}")


# ══════════════════════════════════════════════════════════════
#  STEP 1 — CALCULATE RAW RFM VALUES
# ══════════════════════════════════════════════════════════════
print("\n[STEP 1] Calculating Recency, Frequency, Monetary...")

# Reference date = 1 day after the last order in dataset
SNAPSHOT_DATE = flat["order_date"].max() + pd.Timedelta(days=1)
print(f"  Snapshot date: {SNAPSHOT_DATE.date()}")

rfm = (
    flat.groupby("customer_id")
    .agg(
        last_order_date = ("order_date", "max"),          # for Recency
        frequency       = ("order_id",   "nunique"),      # unique orders
        monetary        = ("revenue",    "sum"),           # total spend
    )
    .reset_index()
)

# Recency = days since last purchase (lower is better → recent customer)
rfm["recency"] = (SNAPSHOT_DATE - rfm["last_order_date"]).dt.days

print(f"\n  RFM raw stats:")
print(f"  {'Recency':<12} min={rfm['recency'].min():>5}  max={rfm['recency'].max():>5}  median={rfm['recency'].median():>6.0f}")
print(f"  {'Frequency':<12} min={rfm['frequency'].min():>5}  max={rfm['frequency'].max():>5}  median={rfm['frequency'].median():>6.0f}")
print(f"  {'Monetary':<12} min={rfm['monetary'].min():>5.0f}  max={rfm['monetary'].max():>5.0f}  median={rfm['monetary'].median():>6.0f}")


# ══════════════════════════════════════════════════════════════
#  STEP 2 — SCORE EACH DIMENSION (1–5)
#  Use pd.qcut to split into 5 equal-sized quantile buckets
# ══════════════════════════════════════════════════════════════
print("\n[STEP 2] Scoring R, F, M on 1-5 scale...")

# Recency:  LOWER days = BETTER → score 5 for lowest recency
rfm["R_score"] = pd.qcut(rfm["recency"], q=5,
                          labels=[5, 4, 3, 2, 1]).astype(int)

# Frequency: HIGHER = BETTER → score 5 for highest frequency
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5,
                          labels=[1, 2, 3, 4, 5]).astype(int)

# Monetary:  HIGHER = BETTER → score 5 for highest spend
rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5,
                          labels=[1, 2, 3, 4, 5]).astype(int)

# Combined RFM score (string like "555", "321")
rfm["RFM_score"] = (
    rfm["R_score"].astype(str) +
    rfm["F_score"].astype(str) +
    rfm["M_score"].astype(str)
)

# Total numeric score (3–15, used for sorting)
rfm["RFM_total"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

print(f"  Score distribution (total):\n{rfm['RFM_total'].value_counts().sort_index().to_string()}")


# ══════════════════════════════════════════════════════════════
#  STEP 3 — SEGMENT CLASSIFICATION
#  Business rules based on R and F scores
# ══════════════════════════════════════════════════════════════
print("\n[STEP 3] Classifying customers into segments...")

def classify_rfm(row):
    r = row["R_score"]
    f = row["F_score"]
    m = row["M_score"]
    fm_avg = (f + m) / 2

    if r >= 4 and fm_avg >= 4:
        return "Champions"
    elif r >= 3 and fm_avg >= 3:
        return "Loyal Customers"
    elif r >= 4 and fm_avg < 3:
        return "Potential Loyalists"
    elif r >= 3 and fm_avg < 2:
        return "Promising"
    elif r == 2 and fm_avg >= 3:
        return "At Risk"
    elif r == 1 and fm_avg >= 3:
        return "Cannot Lose Them"
    elif r == 2 and fm_avg < 3:
        return "Hibernating"
    else:
        return "Lost"

rfm["segment"] = rfm.apply(classify_rfm, axis=1)

seg_counts = rfm["segment"].value_counts()
print(f"\n  Segment distribution:")
for seg, cnt in seg_counts.items():
    pct = cnt / len(rfm) * 100
    bar = "█" * int(pct / 2)
    print(f"  {seg:<22}: {cnt:>5} ({pct:>5.1f}%) {bar}")


# ══════════════════════════════════════════════════════════════
#  STEP 4 — SEGMENT STATISTICS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 4] Segment revenue statistics...")

seg_stats = (
    rfm.groupby("segment")
    .agg(
        customer_count  = ("customer_id",   "count"),
        avg_recency     = ("recency",        "mean"),
        avg_frequency   = ("frequency",      "mean"),
        avg_monetary    = ("monetary",        "mean"),
        total_revenue   = ("monetary",        "sum"),
    )
    .round(1)
    .sort_values("total_revenue", ascending=False)
    .reset_index()
)

seg_stats["revenue_share_pct"] = (
    seg_stats["total_revenue"] / seg_stats["total_revenue"].sum() * 100
).round(1)

print(f"\n  {'Segment':<22} {'Customers':>9} {'Avg Spend':>12} {'Revenue Share':>14}")
print("  " + "-" * 60)
for _, row in seg_stats.iterrows():
    print(f"  {row['segment']:<22} {int(row['customer_count']):>9,} "
          f"  ₹{row['avg_monetary']:>9,.0f}    {row['revenue_share_pct']:>6.1f}%")


# ══════════════════════════════════════════════════════════════
#  STEP 5 — EXPORT RFM TABLE
# ══════════════════════════════════════════════════════════════
print("\n[STEP 5] Exporting RFM table...")

rfm_export = rfm[[
    "customer_id", "recency", "frequency", "monetary",
    "R_score", "F_score", "M_score", "RFM_score", "RFM_total", "segment"
]].round(2)

rfm_export.to_csv(os.path.join(CLEAN_DIR, "rfm_segments.csv"), index=False)
seg_stats.to_csv(os.path.join(CLEAN_DIR, "rfm_segment_stats.csv"), index=False)
print("  Saved: rfm_segments.csv")
print("  Saved: rfm_segment_stats.csv")


# ══════════════════════════════════════════════════════════════
#  CHART 11 — RFM Segment Distribution (Horizontal Bar)
# ══════════════════════════════════════════════════════════════
print("\n[Chart 11] RFM Segment Distribution...")

SEG_COLORS = {
    "Champions"          : "#06D6A0",
    "Loyal Customers"    : "#4361EE",
    "Potential Loyalists": "#4CC9F0",
    "Promising"          : "#FFD166",
    "At Risk"            : "#F77F00",
    "Cannot Lose Them"   : "#F72585",
    "Hibernating"        : "#7209B7",
    "Lost"               : "#6C757D",
}

seg_plot = seg_counts.reset_index()
seg_plot.columns = ["segment", "count"]
seg_plot = seg_plot.sort_values("count")
seg_plot["color"] = seg_plot["segment"].map(SEG_COLORS).fillna("#888")

fig, ax = plt.subplots(figsize=(11, 7))
bars = ax.barh(seg_plot["segment"], seg_plot["count"],
               color=seg_plot["color"], edgecolor="none", height=0.65)
for bar, val in zip(bars, seg_plot["count"]):
    pct = val / len(rfm) * 100
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            f"{val:,}  ({pct:.1f}%)", va="center", fontsize=9, color=TEXT_COLOR)
ax.set_title("RFM Customer Segment Distribution", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Number of Customers")
ax.set_xlim(0, seg_plot["count"].max() * 1.3)
ax.grid(True, axis="x", alpha=0.4)
fig.tight_layout()
path = os.path.join(VIZ_DIR, "11_rfm_segments.png")
fig.savefig(path, bbox_inches="tight", facecolor=BG_COLOR)
plt.close(fig)
print("  Saved: visualizations/11_rfm_segments.png")


# ══════════════════════════════════════════════════════════════
#  CHART 12 — Revenue Share by RFM Segment (Donut)
# ══════════════════════════════════════════════════════════════
print("[Chart 12] Revenue Share by Segment...")

seg_rev = seg_stats.sort_values("total_revenue", ascending=False)
colors_donut = [SEG_COLORS.get(s, "#888") for s in seg_rev["segment"]]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(
    seg_rev["total_revenue"],
    labels=seg_rev["segment"],
    autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
    startangle=140,
    colors=colors_donut,
    pctdistance=0.82,
    wedgeprops=dict(width=0.55, edgecolor=BG_COLOR, linewidth=2),
)
for t in texts:   t.set_color(TEXT_COLOR); t.set_fontsize(9)
for at in autotexts: at.set_color("white"); at.set_fontsize(8); at.set_fontweight("bold")
ax.set_title("Revenue Share by Customer Segment", fontsize=15, fontweight="bold", pad=15)
fig.tight_layout()
path = os.path.join(VIZ_DIR, "12_rfm_revenue_share.png")
fig.savefig(path, bbox_inches="tight", facecolor=BG_COLOR)
plt.close(fig)
print("  Saved: visualizations/12_rfm_revenue_share.png")


# ══════════════════════════════════════════════════════════════
#  CHART 13 — RFM Scatter Plot (Frequency vs Monetary, colored by Segment)
# ══════════════════════════════════════════════════════════════
print("[Chart 13] RFM Scatter Plot...")

fig, ax = plt.subplots(figsize=(11, 7))
for seg, grp in rfm.groupby("segment"):
    ax.scatter(grp["frequency"], grp["monetary"],
               alpha=0.45, s=18, color=SEG_COLORS.get(seg, "#888"),
               label=seg, edgecolors="none")
ax.set_xlabel("Purchase Frequency (# Orders)")
ax.set_ylabel("Total Monetary Value (₹)")
ax.yaxis.set_major_formatter(
    plt.matplotlib.ticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
ax.set_title("Customer Segments: Frequency vs Monetary Spend", fontsize=15, fontweight="bold", pad=15)
ax.legend(fontsize=9, markerscale=1.8, framealpha=0.6)
ax.grid(True, alpha=0.3)
fig.tight_layout()
path = os.path.join(VIZ_DIR, "13_rfm_scatter.png")
fig.savefig(path, bbox_inches="tight", facecolor=BG_COLOR)
plt.close(fig)
print("  Saved: visualizations/13_rfm_scatter.png")


print("\n" + "=" * 60)
print("  Phase 4 COMPLETE — RFM segmentation done!")
print(f"  Total customers segmented: {len(rfm):,}")
print(f"  Champions: {(rfm['segment']=='Champions').sum():,} customers")
print(f"  At Risk  : {(rfm['segment']=='At Risk').sum():,} customers")
print(f"  Lost     : {(rfm['segment']=='Lost').sum():,} customers")
print("=" * 60)
