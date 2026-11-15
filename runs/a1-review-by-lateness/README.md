# Avaloka mission `8d8b6f5f1c18`

**Goal:** average review_score by is_late

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

- is_late=0: mean review_score=4.29.
- is_late=1: mean review_score=2.27.

## Limitations

- Estimated manual effort and value are heuristics pending customer calibration.

## Reproduce

```bash
avaloka analyze /mnt/e/Avloka/data/prepared/orders_analysis.csv --goal 'average review_score by is_late' --output ./reproduced-analysis
```

---
_Reproduce or adapt this mission with `avaloka`._