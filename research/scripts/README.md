# Research Scripts Scaffold

Each module below mirrors a component from `docs/overview.md`. Leave the implementations for later, but keep the interfaces stable so notebooks and the Lean algorithm can import the same helpers.

| Module | Purpose | Notes |
|--------|---------|-------|
| `data_loader.py` | Wrap QuantConnect `History`/API calls, record query params, and handle normalization/QC checks. | Start with structs/dataclasses describing feeds; add fetch functions when data work begins. |
| `feature_store.py` | Canonical feature definitions, metadata, versioning helpers. | Include stubs for registering features and parity tests. |
| `signals/` | Individual signal/alpha functions plus ensemble utilities. | Split deterministic vs ML/RL as needed; export registry for Lean. |
| `portfolio.py` | Allocator and sizing logic (vol targeting, Kelly, constraints). | Provide a base `Allocator` class so experiments can subclass. |
| `risk.py` | Risk guards, VaR/ES calculators, kill-switch helpers. | Mirror Lean `RiskManagementModel` semantics to ease integration. |
| `execution.py` | Schedulers, routing heuristics, OMS helpers. | Make functions accept generic target deltas + market microstructure inputs. |
| `reporting.py` | Post-trade analytics, TCA, attribution routines. | Ensure outputs can feed dashboards/monitoring. |
| `backtest_runner.py` | Wrapper for Lean CLI / QC Cloud backtests with parameter injection. | Should accept config path + overrides and archive outputs. |
| `monitoring.py` | Health checks, alert definitions, runtime metric collectors. | Tie into Lean runtime statistics or external telemetry. |
| `crypto/` | Funding, basis, custody utilities specific to digital assets. | Keep venue-specific quirks isolated here. |

Add docstrings/TODOs inside each module as you begin implementing them so future contributors know the intended interfaces.
