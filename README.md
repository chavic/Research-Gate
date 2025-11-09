# Research Gate

Algorithmic-trading R&D workspace built on QuantConnect Lean. The repo is structured so research notebooks, reusable Python modules, and the live algorithm share the same contracts across the full lifecycle:

```txt
Data → Features → Signal → Portfolio/Size → Risk Filters → Execution → Post‑Trade & Feedback
           ↑ Research & Validation / Monitoring & Ops overlay every stage ↑
```

## Repository Layout

| Path | Description |
|------|-------------|
| `main.py` | Lean algorithm entrypoint. Instantiates adapters, feature engine, signal model, allocator, risk guard, execution planner. |
| `config.json` | QuantConnect project metadata and runtime parameters (set `exchange_venue`, seeds, etc.). |
| `docs/overview.md` | Detailed blueprint for every lifecycle component. Keep it in sync with the implementation. |
| `docs/specs/` | Component specs (data layer, signals, risk, execution). |
| `docs/runbooks/` | Operational procedures (ops monitoring, kill-switch, post-trade, custody). |
| `research/notebooks/` | Pillar hubs (data, features, signals, portfolio, risk, execution, post-trade, research infra, monitoring, crypto) plus legacy idea-bank notebooks. |
| `research/scripts/` | Reusable modules (`data_loader`, `feature_store`, `signals`, `portfolio`, `risk`, `execution`, `costs`, etc.). Import these from both notebooks and `main.py`. |
| `research/research_log.md` | Evidence log for experiments (date, notebook, config, findings, next steps). |

## Quick Start

1. **Install Lean CLI** and authenticate with QuantConnect Cloud.
2. **Run a backtest** (local or cloud):

   ```bash
   # From the repo root
   lean cloud backtest "Research Gate"
   ```

   Use project name from `config.json`. Pass `--parameter exchange_venue=binance` etc. to test other venues.
3. **Inspect outputs**: Lean CLI prints the backtest URL and summary stats. Logs, charts, and JSON live under `./backtests/` (local) or on QuantConnect.

## Research Workflow

1. **Plan**: Read `docs/overview.md` to see which component you’re touching (data, feature, signal, allocator, risk, execution, post-trade, monitoring, crypto).
2. **Prototype in notebooks**: Use the relevant hub under `research/notebooks/`. Import helpers from `research/scripts/` so notebooks and Lean share the same code.
3. **Promote reusable code**: Once an experiment stabilizes, move the logic into a script module (e.g., new signal goes into `research/scripts/signals/`). Update `main.py` to instantiate the new class.
4. **Validate**: Run Lean backtests (historical periods, assets, regimes) and record findings in `research/research_log.md` with config hashes/parameters.
5. **Operationalize**: Update specs/runbooks if you change assumptions (fees, risk limits, execution tactics). Ensure monitoring/post-trade tooling can digest the new outputs.

## Key Practices

- **Contracts first**: Every component implements a simple contract (`SignalModel.score`, `Allocator.compute`, `RiskGuard.evaluate`, `ExecutionPlanner.plan`). This keeps research swappable.
- **Log parameters**: Use `DataLoader`/`FeatureRegistry` to capture query specs and feature metadata for reproducibility.
- **Realism**: Set the brokerage model (`SetBrokerageModel`) and attach realistic fees/slippage (`TieredCryptoFeeModel`). Plug in risk guards before scheduling orders.
- **Documentation**: When you add or change a capability, update the relevant spec/runbook and drop a note in the research log.

## Next Steps

- Populate the stub notebooks (data, features, portfolio, execution, post-trade, research infra, monitoring, crypto) with actual experiments.
- Flesh out the script modules with production-quality code (loaders, feature builders, signal models, allocators, risk overlays, schedulers, TCA).
- Extend `main.py` to use the new research components as they mature, replacing the placeholder random strategy.

Questions or onboarding? Start with `docs/overview.md`, then explore the notebook hubs that match your focus area.
