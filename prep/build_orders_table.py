"""Build one row per order from the nine Olist tables.

Why this exists: the Olist tables have different grains. `orders` has one row
per order, `order_items` one row per item, `order_payments` one row per payment
instalment record, and `order_reviews` sometimes several rows per order. Joining
them directly duplicates orders and inflates every average. This script
aggregates each child table to the order level first, then joins, and asserts
the row count never changes.

Run (inside WSL, with the Avaloka venv active):
    python /mnt/e/Avloka/prep/build_orders_table.py

Output: data/prepared/orders_enriched.csv and .parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "olist"
OUT = ROOT / "data" / "prepared"

ORDER_DATES = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def load(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv", encoding="utf-8-sig", **kwargs)


def build_base() -> pd.DataFrame:
    """Everything except the lateness definition. One row per order."""
    orders = load("olist_orders_dataset", parse_dates=ORDER_DATES)
    customers = load("olist_customers_dataset")
    items = load("olist_order_items_dataset")
    products = load("olist_products_dataset")
    categories = load("product_category_name_translation")
    sellers = load("olist_sellers_dataset")
    payments = load("olist_order_payments_dataset")
    reviews = load("olist_order_reviews_dataset", parse_dates=["review_answer_timestamp"])
    n_orders = len(orders)

    # --- items: enrich each item, then collapse to one row per order ---------
    items = (
        items.merge(products[["product_id", "product_category_name", "product_weight_g"]],
                    on="product_id", how="left")
             .merge(categories, on="product_category_name", how="left")
             .merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")
    )
    items["category"] = (
        items["product_category_name_english"]
        .fillna(items["product_category_name"])
        .fillna("unknown")
    )
    item_totals = items.groupby("order_id").agg(
        n_items=("order_item_id", "size"),
        n_sellers=("seller_id", "nunique"),
        items_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        total_weight_g=("product_weight_g", lambda s: s.sum(min_count=1)),
    )
    # The "main" item of an order is its most expensive one.
    main_item = (
        items.sort_values(["order_id", "price"], ascending=[True, False])
             .drop_duplicates("order_id")
             .set_index("order_id")[["category", "seller_state"]]
             .rename(columns={"category": "main_category"})
    )

    # --- payments: total paid, and the payment type that carried the most ----
    pay_totals = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        max_installments=("payment_installments", "max"),
    )
    main_pay = (
        payments.sort_values(["order_id", "payment_value"], ascending=[True, False])
                .drop_duplicates("order_id")
                .set_index("order_id")[["payment_type"]]
    )

    # --- reviews: keep the most recent review per order ---------------------
    review = (
        reviews.sort_values("review_answer_timestamp")
               .groupby("order_id")
               .agg(review_score=("review_score", "last"), n_reviews=("review_id", "size"))
    )

    # --- join everything onto orders; each join must stay one row per order --
    df = orders.merge(
        customers[["customer_id", "customer_city", "customer_state"]],
        on="customer_id", how="left", validate="one_to_one",
    )
    for child in (item_totals, main_item, pay_totals, main_pay, review):
        df = df.merge(child, left_on="order_id", right_index=True, how="left",
                      validate="one_to_one")
    assert len(df) == n_orders, f"join changed the row count: {len(df)} != {n_orders}"
    assert df["order_id"].is_unique

    # --- features known at purchase time (safe to use for prediction) --------
    purchase = df["order_purchase_timestamp"]
    df["purchase_month"] = purchase.dt.strftime("%Y-%m")
    df["purchase_weekday"] = purchase.dt.day_name()
    df["purchase_hour"] = purchase.dt.hour
    df["promised_days"] = (df["order_estimated_delivery_date"] - purchase).dt.total_seconds() / 86400
    df["same_state"] = df["customer_state"] == df["seller_state"]
    df["freight_share"] = df["freight_value"] / (df["items_value"] + df["freight_value"])

    # --- known only after the fact (these LEAK the outcome; never train on them)
    df["approval_hours"] = (df["order_approved_at"] - purchase).dt.total_seconds() / 3600
    df["handling_days"] = (df["order_delivered_carrier_date"] - purchase).dt.total_seconds() / 86400
    df["actual_days"] = (df["order_delivered_customer_date"] - purchase).dt.total_seconds() / 86400
    return df


def add_lateness(df: pd.DataFrame) -> pd.DataFrame:
    """Add `is_late` and `days_late`. This definition is the heart of the analysis.

    Must add two columns and return the frame:
      is_late    True / False, or <NA> where lateness is undefined for that order
      days_late  number of days past the promised date (your choice whether early
                 deliveries are negative or clipped to 0); NaN where undefined

    Columns you will need:
      order_status                    delivered / shipped / canceled / unavailable / ...
      order_delivered_customer_date   timestamp with a time of day; NaT if never delivered
      order_estimated_delivery_date   the promise shown to the customer; always midnight

    Definition used here:
      1. Lateness is defined only for orders that were actually delivered.
         Canceled / unavailable / still-in-transit orders get <NA>: they are a
         different failure ("never arrived"), and counting them as late would
         inflate the late rate.
      2. Calendar dates are compared, not timestamps. The promise is a date
         (always midnight), so a parcel arriving at 2 PM on the promised day is
         on time.
      3. `days_late` is negative for early deliveries, so the effect of arriving
         early on review score stays visible.
    """
    delivered = df["order_delivered_customer_date"]
    promised = df["order_estimated_delivery_date"]
    defined = (df["order_status"] == "delivered") & delivered.notna()

    days = (delivered.dt.normalize() - promised.dt.normalize()).dt.days
    df["days_late"] = days.where(defined)
    df["is_late"] = (days > 0).astype("boolean").where(defined)
    return df


def main() -> int:
    df = build_base()
    print(f"base table: {len(df):,} orders x {df.shape[1]} columns (one row per order: OK)")
    print(f"  orders with no items:   {df['n_items'].isna().sum():,}")
    print(f"  orders with no review:  {df['review_score'].isna().sum():,}")
    print(f"  orders with >1 review:  {(df['n_reviews'] > 1).sum():,}")
    print(f"  never delivered:        {df['order_delivered_customer_date'].isna().sum():,}")

    try:
        df = add_lateness(df)
    except NotImplementedError as exc:
        print(f"\nSTOPPED: {exc}. Nothing was written.")
        return 2

    missing = {"is_late", "days_late"} - set(df.columns)
    assert not missing, f"add_lateness must add: {missing}"
    defined = df["is_late"].notna()
    late = df.loc[defined, "is_late"].astype(bool)
    print(f"\nlateness defined for {defined.sum():,} orders; late rate {late.mean():.2%}")
    print("mean review score:")
    print(df.loc[defined].groupby(late)["review_score"].agg(["mean", "count"]).round(3).to_string())

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "orders_enriched.csv", index=False)
    df.to_parquet(OUT / "orders_enriched.parquet", index=False)
    print(f"\nwrote {OUT / 'orders_enriched.csv'} and .parquet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
