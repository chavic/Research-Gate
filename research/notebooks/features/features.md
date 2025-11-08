# Feature Engineering Notebook Hub

## Mission
Turn normalized events into deterministic, versioned features (technical indicators, microstructure stats, ML labels) that stay in sync between research and Lean.

## Initial Notebook Targets
- `feature_catalog.ipynb` – inventory of rolling statistics, volatility/ATR, spreads, imbalance, and seasonal features.
- `feature_parity.ipynb` – offline vs live parity tests using `History` priming + live consolidators.
- `labeling_lab.ipynb` – horizon return, hit-rate, and classification target definitions for ML/RL workflows.

## Research Checklist
- Specify indicator/window parameters, decay cadences, and null-handling in a feature registry table.
- Capture serialization/version IDs so Lean modules know which feature set they consume.
- Promote reusable computations into `research/scripts/feature_store.py` and keep notebooks focused on experiments.
