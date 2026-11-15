# What does a late delivery cost? An Avaloka analysis of 96,470 Olist orders

**Avaloka Engineering Intern Hackathon, 14–15 Nov 2026**

**Question asked:** *What drives late deliveries on Olist, and how much does a late
delivery cost in review score?*

**Tool:** Avaloka open-source CLI 1.6.0 (`avaloka analyze`, `avaloka train`), run
locally with no LLM. Every descriptive number Avaloka returned was re-computed
independently from the raw CSVs; the model scores were not.

**Dataset:** [Olist Brazilian E-Commerce](https://github.com/olist/work-at-olist-data/tree/master/datasets)
(MIT licence), 9 tables, 99,441 orders, 2016–2018.

## What Avaloka found

1. **6.8% of delivered orders arrive late** (6,534 of 96,470), and late orders
   are rated **2.27 stars against 4.29** for on-time orders: a two-star drop.
2. **Lateness is geographic.** The worst states are in the north-east:
   Alagoas 21.4%, Maranhão 17.4%, Sergipe 15.2%. São Paulo, the largest
   market, is at 4.5%.
3. **It spikes in specific months:** 19.0% in March 2018, 14.1% in February
   2018 and 12.4% in November 2017 (Black Friday), against 4.4% in the
   median month.
4. **Lateness is only partly predictable at checkout.** Using only what is
   known when the order is placed, Avaloka's best model (gradient boosting)
   reaches ROC AUC 0.709 ± 0.011 against a 0.500 baseline.
5. **Avaloka's leakage check missed a leak split across two columns** and
   certified a ROC AUC 1.000 model as deployable. Details under
   [What broke](#what-broke-or-was-confusing).

The damage grows with the delay (my own computation on the prepared table):

| Delivery | Mean review | Orders |
| --- | --- | --- |
| Early | 4.29 | 88,163 |
| On the promised day | 4.03 | 1,280 |
| 1–3 days late | 3.29 | 1,852 |
| 4–7 days late | 2.10 | 1,748 |
| 8–14 days late | 1.67 | 1,446 |
| 15+ days late | 1.72 | 1,335 |

This is an association in observational data. Late orders may differ from
on-time ones in other ways (remote customers, bulky products), so the two-star
gap is an upper bound on what fixing lateness alone would recover.

## Verification: Avaloka against an independent recomputation

[`prep/verify_avaloka.py`](prep/verify_avaloka.py) recomputes each number from
the raw CSVs with Python's `csv` module and plain string dates. It shares no
code with the pandas pipeline that fed Avaloka.

| Metric | Avaloka | Independent | Match |
| --- | --- | --- | --- |
| Delivered orders analysed | 96,470 | 96,470 | yes |
| Mean review score, on-time | 4.290 | 4.290 | yes |
| Mean review score, late | 2.270 | 2.270 | yes |
| Late rate, Alagoas (AL) | 0.2141 | 0.2141 | yes |
| Late rate, Maranhão (MA) | 0.1743 | 0.1743 | yes |
| Late rate, March 2018 | 0.190 | 0.1896 | yes |
| Late rate, February 2018 | 0.141 | 0.1413 | yes |
| Late rate, November 2017 | 0.124 | 0.1240 | yes |
| Late rate, São Paulo (SP) | not returned | 0.0449 | see finding 3 below |

Every number Avaloka returned was correct. The join was also checked: the
order-level table has exactly 99,441 rows, and its item, freight and payment
totals equal the raw files to the cent.

## How it was done

| Step | What | Where |
| --- | --- | --- |
| 1 | Aggregate items, payments and reviews to one row per order, then join | [`prep/build_orders_table.py`](prep/build_orders_table.py) |
| 2 | Define lateness (below) and derive model tables | [`prep/build_model_tables.py`](prep/build_model_tables.py) |
| 3 | `avaloka analyze` × 4 | `runs/a1` … `runs/a4` |
| 4 | `avaloka train` on purchase-time features only | `runs/m1-predict-late-honest` |
| 5 | `avaloka train` with a deliberately leaky feature | `runs/m2-predict-late-leaky` |
| 6 | Independent verification | [`prep/verify_avaloka.py`](prep/verify_avaloka.py) |

**Lateness definition.** An order is late if it was delivered on a calendar day
after the promised date. Only delivered orders count; the 2,971 orders that
were cancelled, unavailable or still in transit are excluded, not counted as
late. Calendar dates are compared because the promise is a date, so a parcel
arriving at 2 PM on the promised day is on time.

**Prompts given to Avaloka**

```
avaloka analyze orders_analysis.csv --goal "average review_score by is_late"
avaloka analyze orders_analysis.csv --goal "average is_late by customer_state"
avaloka analyze orders_analysis.csv --goal "monthly trend of is_late by purchase_month"
avaloka analyze orders_analysis.csv --goal "average is_late by purchase_month"
avaloka train   orders_model.csv  --target is_late
avaloka train   orders_leaky.csv  --target is_late
```

Each run folder holds Avaloka's `executive_report.html`, `goal_analysis.json`,
`validation_report.json`, `lineage.json` and the generated `analysis.py`.

## What broke or was confusing

### 1. `avaloka train` crashes on a single blank text cell

One missing value in any text column stops training with
`TypeError: boolean value of NA is ambiguous`. The message then suggests
"ragged rows, mixed delimiters or an unusual encoding", which is not the cause.
It reproduces on Avaloka's own example file:

```bash
python -c "import pandas as pd; d=pd.read_csv('avaloka/examples/churn.csv'); d.loc[0,'contract']=None; d.to_csv('churn_blank.csv',index=False)"
avaloka train churn_blank.csv --target churned
```

The traceback ends in scikit-learn's `SimpleImputer` (`_object_dtype_isnan`,
`X != X`): the text column reaches the imputer holding `pandas.NA`, which
cannot be compared. Workaround used here: fill text blanks with `"unknown"`
before training. In Olist this was triggered by 1 order out of 96,470 with no
payment type.

### 2. The leakage check passes a leak that is split across two columns

`orders_leaky.csv` adds `actual_days` (days from purchase to delivery, known
only after delivery) to a table that already has `promised_days`. Together
they define the target: `is_late` is essentially `actual_days > promised_days`.

Avaloka's result:

- best model `logistic_regression`, **ROC AUC 1.000**
- `target_leakage: pass` — "No feature is near-perfectly predictive of the target"
- **Validation verdict PASS, max safe deployment level 4/4**

The check appears to test features one at a time (`actual_days` alone
correlates 0.60 with the target), so a leak that needs two columns gets
through. A perfect score on a real-world target is itself a signal worth a
warning. This was tested on the open-source CLI only, not the hosted platform.

### 3. Grouped answers are silently cut to 10 groups

"average is_late by customer_state" returned 10 of 27 states, and the month
comparison 10 of 23 months, with nothing in the output saying it was truncated.
São Paulo, the largest state, is missing. The top-ranked month was `2016-09`
at 100% late, which is a single order; no sample-size warning was shown.

### 4. Smaller points

- "monthly trend of is_late by purchase_month" came back `limited` because the
  `YYYY-MM` text column was not recognised as a date. Reporting `limited`
  instead of guessing is the right behaviour, but the same run still printed
  "Validation verdict: PASS", which reads as if the question was answered.
- The terminal summary prints counts in scientific notation
  (`count rows=1.11e+03` for 1,107 orders). Exact values are in
  `goal_analysis.json`.
- `scripts/install.sh` installs the full platform (PyTorch, Ray, MLflow). The
  CLI itself needs only `pip install -e ".[formats]"`, which is 465 MB and
  enough for `analyze` and `train`.

## Reproduce

```bash
git clone https://github.com/guruvaidev/avaloka.git && cd avaloka
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[formats]"

# from this repo, after downloading the 9 Olist CSVs into data/olist/
python prep/build_orders_table.py
python prep/build_model_tables.py
python prep/verify_avaloka.py
```
