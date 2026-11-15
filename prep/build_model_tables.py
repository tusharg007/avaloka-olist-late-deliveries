"""Derive the two tables used for `avaloka train` from orders_enriched.

orders_model.csv   only features known at purchase time + the target `is_late`
orders_leaky.csv   the same, plus `actual_days` (known only after delivery).
                   This one exists to test whether Avaloka's integrity check
                   refuses to train on a feature that gives the answer away.

Only delivered orders are kept, because lateness is undefined for the rest.
"""
from pathlib import Path

import pandas as pd

PREP = Path(__file__).resolve().parents[1] / "data" / "prepared"

PURCHASE_TIME_FEATURES = [
    "customer_state", "seller_state", "same_state", "main_category",
    "n_items", "n_sellers", "items_value", "freight_value", "freight_share",
    "total_weight_g", "payment_type", "max_installments",
    "purchase_weekday", "purchase_hour", "promised_days",
]

df = pd.read_parquet(PREP / "orders_enriched.parquet")
df = df[df["is_late"].notna()].copy()
df["is_late"] = df["is_late"].astype(int)
df["same_state"] = df["same_state"].astype(int)

# Workaround for an Avaloka 1.6.0 bug: `avaloka train` crashes with
# "TypeError: boolean value of NA is ambiguous" when a text column has a
# missing value (here: 1 order with no payment_type). Fill text blanks.
text_cols = df[PURCHASE_TIME_FEATURES].select_dtypes(include=["object", "string"]).columns
df[text_cols] = df[text_cols].fillna("unknown")

df[PURCHASE_TIME_FEATURES + ["is_late"]].to_csv(PREP / "orders_model.csv", index=False)
df[PURCHASE_TIME_FEATURES + ["actual_days", "is_late"]].to_csv(PREP / "orders_leaky.csv", index=False)

# Analysis table: delivered orders, numeric is_late, review score included.
keep = PURCHASE_TIME_FEATURES + ["purchase_month", "days_late", "review_score", "is_late"]
df[keep].to_csv(PREP / "orders_analysis.csv", index=False)

print(f"{len(df):,} delivered orders; late rate {df['is_late'].mean():.2%}")
for name in ("orders_model.csv", "orders_leaky.csv", "orders_analysis.csv"):
    print(f"  wrote {name} ({(PREP / name).stat().st_size / 1e6:.1f} MB)")
