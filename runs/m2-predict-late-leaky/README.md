# Avaloka mission `aa60e82b0379`

**Goal:** Predict 'is_late'

This bundle was produced by Avaloka as a governed *Data Mission* — an outcome, not an interaction. Economic multiplier: **11.1x** (≈20.1 manual hours compressed).

## Deliverables

- `executive_report.html` — the decision-maker summary
- `technical_report.html` — full methodology, schema, quality and validation
- `analysis.ipynb` / `analysis.py` — reproducible pipeline
- `transformed_dataset.parquet` — cleaned working dataset
- `data_quality.json`, `validation_report.json`, `planner_graph.json` — evidence
- `assumptions.yaml`, `lineage.json`, `environment.lock` — governance & reproducibility
- `model/` + `model_card.md` — the validated model and its card
- `evaluation_report.html`, `cost_quality.json` — candidate comparison & economics
- `service.py`, `Dockerfile`, `deployment/` — the deployment package
- `feature_contract.yaml`, `inference_schema.json`, `monitoring_config.yaml` — the serving contract

## Key findings

- 'freight_value' and 'total_weight_g' are strongly associated (|corr|=0.6347).
- 'actual_days' and 'is_late' are strongly associated (|corr|=0.604).
- Best model 'logistic_regression' scored 1.0000 roc_auc on holdout.
- 'freight_value' and 'total_weight_g' move together (|corr|=0.6347); consider redundancy or a shared driver.

## Limitations

- Estimated manual effort and value are heuristics pending customer calibration.

## Reproduce

```bash
python analysis.py  # reproduce data preparation
```

## Serve locally

```bash
pip install -r requirements.lock
uvicorn service:app --port 8080
# then: avaloka deploy . --target local
```

---
_Reproduce or adapt this mission with `avaloka`._