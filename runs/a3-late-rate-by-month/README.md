# Avaloka mission `3a01d6209ece`

**Goal:** monthly trend of is_late by purchase_month

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

- A time trend cannot be calculated: no date/time column was identified.

## Limitations

- The stated goal was not fully answered by a supported calculation; see goal_analysis.json for the reason.
- Estimated manual effort and value are heuristics pending customer calibration.

## Reproduce

```bash
avaloka analyze /mnt/e/Avloka/data/prepared/orders_analysis.csv --goal 'monthly trend of is_late by purchase_month' --output ./reproduced-analysis
```

---
_Reproduce or adapt this mission with `avaloka`._