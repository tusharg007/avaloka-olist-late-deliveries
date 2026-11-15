# Model card — Predict 'is_late'

- **Mission:** `b04be9af3831`
- **Task:** binary_classification
- **Target:** is_late
- **Primary metric:** roc_auc
- **Selected model:** gradient_boosting
- **Validation verdict:** PASS (max safe deployment level 4/4)

## Intended use

Decision support for the stated goal. Not a substitute for human judgement on high-stakes decisions.

## Performance

| Candidate | roc_auc | CV mean ± std |
|---|---|---|
| gradient_boosting | 0.7087 | 0.709 ± 0.011 |
| logistic_regression | 0.6969 | 0.701 ± 0.011 |
| random_forest | 0.6844 | 0.692 ± 0.005 |

## Training data

- Rows: 77153 train / 19289 test
- Features: 15

## Limitations & ethical considerations

- Estimated manual effort and value are heuristics pending customer calibration.

## Validation checks

- **data_sufficiency** — PASS: ~50 rows/feature suggests >= 750 rows for 15 features.
- **target_leakage** — PASS: No feature is near-perfectly predictive of the target.
- **split_validity** — PASS: Used 'stratified_train_test' (77153 train / 19289 test rows).
- **beats_baseline** — PASS: CV roc_auc 0.709 beats the prior baseline (0.500) by more than fold noise.
- **stability** — PASS: CV roc_auc = 0.709 +/- 0.011 (stable).
- **overfitting** — PASS: Holdout and CV scores are consistent.
