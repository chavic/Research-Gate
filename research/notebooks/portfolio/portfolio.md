# Portfolio & Sizing Notebook Hub

## Mission
Translate signal outputs into target exposures that respect volatility/ES/DD budgets, leverage caps, borrow limits, and liquidity constraints before trades are staged.

## Initial Notebook Targets
- `allocator.ipynb` – volatility targeting, tempered Kelly, and utility-based sizing comparisons.
- `constraint_playbook.ipynb` – gross/net, sector, leverage, correlation, and borrow availability constraint prototyping.
- `capacity_turnover.ipynb` – turnover vs capacity studies and ADV/participation guardrail tuning.

## Research Checklist
- Define the interface between signals (scores/confidence) and allocators (weights/quantities) so Lean’s `SetPortfolioConstructionModel` or custom classes can consume them.
- Record covariance/β estimation choices and refresh cadences; ensure these inputs are reproducible in production.
- Export any reusable optimizers/sizers to `research/scripts/portfolio.py` for integration with `main.py`.
