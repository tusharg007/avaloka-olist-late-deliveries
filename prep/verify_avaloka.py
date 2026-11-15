"""Recompute Avaloka's headline numbers straight from the raw Olist CSVs.

Deliberately shares no code with build_orders_table.py: it uses the csv module
and plain string dates, so an error in the pandas pipeline cannot hide here.
Compares against the goal_analysis.json that each Avaloka run wrote.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "olist"
RUNS = ROOT / "runs"


def rows(name):
    with open(RAW / f"{name}.csv", encoding="utf-8-sig", newline="") as fh:
        yield from csv.DictReader(fh)


state = {r["customer_id"]: r["customer_state"] for r in rows("olist_customers_dataset")}

# Latest review per order (by answer timestamp), same rule as the main table.
latest = {}
for r in rows("olist_order_reviews_dataset"):
    key = r["order_id"]
    if key not in latest or r["review_answer_timestamp"] >= latest[key][0]:
        latest[key] = (r["review_answer_timestamp"], int(r["review_score"]))

late_by_state = defaultdict(lambda: [0, 0])     # state -> [late, total]
score = {0: [0, 0], 1: [0, 0]}                  # is_late -> [sum, count]
n = n_late = 0
for o in rows("olist_orders_dataset"):
    if o["order_status"] != "delivered" or not o["order_delivered_customer_date"]:
        continue
    is_late = int(o["order_delivered_customer_date"][:10] > o["order_estimated_delivery_date"][:10])
    n += 1
    n_late += is_late
    s = late_by_state[state[o["customer_id"]]]
    s[0] += is_late
    s[1] += 1
    if o["order_id"] in latest:
        score[is_late][0] += latest[o["order_id"]][1]
        score[is_late][1] += 1


def avaloka(run):
    g = json.load(open(RUNS / run / "goal_analysis.json", encoding="utf-8"))
    return {str(x["group"]): x["value"] for x in g["metrics"]["groups"]}


a1 = avaloka("a1-review-by-lateness")
a2 = avaloka("a2-late-rate-by-state")
table = [
    ("Delivered orders analysed", "96,470 (run scope)", f"{n:,}"),
    ("Mean review score, on-time", f"{a1['0']:.3f}", f"{score[0][0] / score[0][1]:.3f}"),
    ("Mean review score, late", f"{a1['1']:.3f}", f"{score[1][0] / score[1][1]:.3f}"),
]
for st in ("AL", "MA", "SP"):
    late, total = late_by_state[st]
    got = f"{a2[st]:.4f}" if st in a2 else "not in output"
    table.append((f"Late rate, state {st}", got, f"{late / total:.4f}"))

print(f"overall late rate (independent): {n_late / n:.4%} ({n_late:,} of {n:,})")
print(f"states in Avaloka output: {len(a2)} of {len(late_by_state)} in the data")
print(f"{'Metric':32} {'Avaloka':>20} {'Independent':>14}  Match")
for name, av, mine in table:
    try:
        ok = abs(float(av) - float(mine)) < 5e-4
    except ValueError:
        ok = av.split()[0] == mine
    print(f"{name:32} {av:>20} {mine:>14}  {'yes' if ok else 'NO'}")
