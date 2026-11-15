# Avaloka mission `e4ff82cfa675`

**Goal:** average is_late by purchase_month

This bundle was produced by Avaloka as a governed *Data Mission* — an outcome, not an interaction. Economic multiplier: **11.1x** (≈12.4 manual hours compressed).

## Deliverables

- `executive_report.html` — the decision-maker summary
- `technical_report.html` — full methodology, schema, quality and validation
- `analysis.ipynb` / `analysis.py` — reproducible pipeline
- `transformed_dataset.parquet` — cleaned working dataset
- `data_quality.json`, `validation_report.json`, `planner_graph.json` — evidence
- `assumptions.yaml`, `lineage.json`, `environment.lock` — governance & reproducibility
- `goal_analysis.json` — measured answer to the stated goal

## Key findings

- purchase_month=2016-09: mean is_late=1.
- purchase_month=2018-03: mean is_late=0.19.
- purchase_month=2018-02: mean is_late=0.141.
- purchase_month=2017-11: mean is_late=0.124.
- purchase_month=2017-12: mean is_late=0.0746.

## Limitations

- Estimated manual effort and value are heuristics pending customer calibration.

## Reproduce

```bash
avaloka analyze /mnt/e/Avloka/data/prepared/orders_analysis.csv --goal 'average is_late by purchase_month' --output ./reproduced-analysis
```

---
_Reproduce or adapt this mission with `avaloka`._