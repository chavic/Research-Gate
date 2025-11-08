# Research & Validation Notebook Hub

## Mission
Provide rigorous validation pipelines—backtests, walk-forward studies, stress tests, and model governance artifacts—that prove a strategy is production ready.

## Initial Notebook Targets
- `walk_forward.ipynb` – rolling/expanding window tests with latency, borrow, and fee modeling parity.
- `scenario_lab.ipynb` – gap moves, vol spikes, liquidity droughts, funding shocks, and basis stress simulations.
- `model_registry.ipynb` – catalog versions, hyper-parameters, seeds, and approval status for each deployed model.

## Research Checklist
- Record engine configurations (`config.json`, fee/slippage/fill model settings) so others can reproduce results exactly.
- Capture statistical significance testing (block/bootstrap, Monte Carlo) and multiple-hypothesis controls.
- Publish validation outputs (plots, JSON summaries) and reference them in `research/research_log.md` for governance.
