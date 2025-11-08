# Signal Combinations Hub

## Notebooks
- `idea_bank_signals_combinations.ipynb` – ensemble frameworks, weighting schemes, hierarchical filters, and testing harness.
- `idea_bank_signals_combinations_backup.ipynb` – snapshot of earlier experiments / spare playground.

## Guidance
- Reference upstream signal definitions in `../signals.md` when wiring ensembles.
- Document assumptions (e.g., normalization, lookback windows) in markdown cells so downstream strategies stay aligned.
- When ensemble logic stabilizes, extract reusable code into `research/scripts/` and reference it from notebooks.
