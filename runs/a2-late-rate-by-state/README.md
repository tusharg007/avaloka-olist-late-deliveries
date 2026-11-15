# Avaloka mission `cf9254428d36`

**Goal:** average is_late by customer_state

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

- customer_state=AL: mean is_late=0.214.
- customer_state=MA: mean is_late=0.174.
- customer_state=SE: mean is_late=0.152.
- customer_state=PI: mean is_late=0.139.
- customer_state=CE: mean is_late=0.138.

## Limitations

- Estimated manual effort and value are heuristics pending customer calibration.

## Reproduce

```bash
avaloka analyze /mnt/e/Avloka/data/prepared/orders_analysis.csv --goal 'average is_late by customer_state' --output ./reproduced-analysis
```

---
_Reproduce or adapt this mission with `avaloka`._