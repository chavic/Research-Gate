# Signal Engine Specification

## Purpose
Describe how we convert features into actionable signals (scores, probabilities, confidence intervals) and expose them to Lean via a stable contract.

## Signal Contract
- Inputs: feature dictionary (`str -> float`) aligned with entries in `FeatureRegistry`.
- Outputs: `(edge, confidence)` tuples, optional metadata such as horizon, regime tags, or expected holding period.
- Interface: `research/scripts/signals.SignalModel` protocol; Lean `main.py` should instantiate concrete models via factories.

## Requirements
- Deterministic rules and ML models must log version IDs, parameter sets, and training data references.
- Regime filters should be modular (compose with signals) and log classification thresholds.
- Signals must surface latency/decay expectations so schedulers know urgency.

## TODO
- Define serialization format for ML weights and deterministic rule configs.
- Document evaluation metrics (Sharpe, hit-rate, information ratio) plus minimum viability thresholds before production consideration.
