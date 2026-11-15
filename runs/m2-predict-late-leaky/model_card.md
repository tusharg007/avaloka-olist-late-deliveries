# Model card — Predict 'is_late'

- **Mission:** `aa60e82b0379`
- **Task:** binary_classification
- **Target:** is_late
- **Primary metric:** roc_auc
- **Selected model:** logistic_regression
- **Validation verdict:** PASS (max safe deployment level 4/4)

## Intended use

Decision support for the stated goal. Not a substitute for human judgement on high-stakes decisions.

## Performance

| Candidate | roc_auc | CV mean ± std |
|---|---|---|
| logistic_regression | 1.0000 | 1.000 ± 0.000 |
| gradient_boosting | 0.9998 | 1.000 ± 0.000 |
| random_forest | 0.9977 | 0.997 ± 0.001 |

## Training data

- Rows: 77176 train / 19294 test
- Features: 16

## Limitations & ethical considerations

- Estimated manual effort and value are heuristics pending customer calibration.

## Validation checks

- **data_sufficiency** — PASS: ~50 rows/feature suggests >= 800 rows for 16 features.
- **target_leakage** — PASS: No feature is near-perfectly predictive of the target.
- **split_validity** — PASS: Used 'stratified_train_test' (77176 train / 19294 test rows).
- **beats_baseline** — PASS: CV roc_auc 1.000 beats the prior baseline (0.500) by more than fold noise.
- **stability** — PASS: CV roc_auc = 1.000 +/- 0.000 (stable).
- **overfitting** — PASS: Holdout and CV scores are consistent.
