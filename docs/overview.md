# Trading Research & Build Blueprint (Lean Focus)

Design everything around the pipeline below. Every component states what problem it solves, what knobs Lean exposes, and the implementation details you must understand before writing code or research.

```txt
Data → Features → Signal → Portfolio/Size → Risk Filters → Execution → Post‑Trade & Feedback
↑             Research & Validation / Monitoring & Ops overlay every stage             ↑
```

---

## 1. Market Data Layer

- **Scope**: venue connectors (exchange/broker APIs, FIX, WebSocket ticks/order book, REST history/ref data), normalization, enrichment, and storage.
- **Lean controls**
  - `AddEquity/AddCrypto/AddForex/...` define feed source, resolution, fill-forward rules, extended hours.
  - `SubscriptionManager.SetDataNormalizationMode`, `SetSecurityInitializer`, and custom `IDataProvider`/`IDataCacheProvider` plug in custom normalization, corp actions, borrow/funding metadata.
  - History layer (`self.History`, `HistoryRequest`, `SubscriptionDataSource`) provides bulk data pulls for research, feature backfills, and diagnostics.
  - Time alignment via `SetTimeZone`, `Security.Exchange.Hours`, and custom calendars.
- **Key details to know**
  - Maintain symbol mapping with Lean `Symbol` objects and inject reference data as needed.
  - Align timezones and exchange calendars; manage fill-forward vs raw tick trade-offs.
  - Handle corporate actions, borrow/funding metadata, and data retention (`./data` or remote providers).
  - Monitor heartbeats/connection status and instrument data health.

---

## 2. Feature Engineering Layer

- **Scope**: transforms (returns, ATR, spreads, imbalance, queue position, seasonality), labels/targets for ML, feature store governance.
- **Lean controls**
  - Built-in indicator library (`RelativeStrengthIndex`, `ExponentialMovingAverage`, consolidators) and custom indicators derived from `IndicatorBase`.
  - Rolling windows (`RollingWindow[T]`), `TradeBarConsolidator`/`QuoteBarConsolidator` for bar aggregation, `RegisterIndicator` for live updates.
  - `History` + pandas/numpy for offline batch features; use `IndicatorExtensions.Of` to pipe bars into indicators.
- **Key details**
  - Warm up indicators using `self.SetWarmUp` or manual history loops to avoid NaNs.
  - Keep parity between research notebooks and Lean runtime environments.
  - Cache feature definitions, handle missing values, and align timestamps across resolutions.

---

## 3. Signal (Alpha) Engine

- **Scope**: deterministic rules (PA, breakouts, stat-arb), probabilistic/ML models (classifiers/regressors/RL), regime filters, state management.
- **Lean controls**
  - Classic pattern: implement logic inside `OnData`.
  - Framework pattern: plug into Alpha Model via `QCAlgorithmFramework` (`AlphaModel.Update`, emit `Insight` objects with direction/magnitude/duration).
  - Custom ML: integrate external libraries (sklearn, PyTorch) in research, export weights, load inside Lean, run inference per bar/tick.
  - Regime detection through stateful indicators, `VolatilityModel`, or custom schedule events.
- **Key details**
  - Maintain per-symbol state dictionaries and throttle logic using `self.Time`.
  - Use `InsightScore`/`InsightDirection` and deterministic seeds for reproducibility.
  - Log feature inputs, predictions, and decisions for audit trails.

---

## 4. Portfolio Construction & Position Sizing

- **Scope**: objective (max return vs risk budget), sizing (fixed fraction, vol targeting, tempered Kelly), constraints (gross/net, leverage, borrow, min lots).
- **Lean controls**
  - Direct mode: `SetHoldings(symbol, weight)` or `Order` functions with custom sizing formulas.
  - Framework mode: `SetPortfolioConstructionModel` (e.g., `EqualWeightingPortfolioConstructionModel`, `OptimizedPortfolioConstructionModel`, or custom class implementing `IPortfolioConstructionModel`) consumes Insights and emits target quantities.
  - Leverage settings via `Security.SetLeverage`, account currency exposures through `Portfolio.TotalPortfolioValue`.
- **Key details**
  - Handle fractional quantities, venue minimums, and leverage constraints.
  - Compute target weights with covariance matrices or custom optimizers.
  - Enforce diversification, gross/net exposure limits, and borrow availability.

---

## 5. Risk Controls (Pre-Trade)

- **Scope**: per-trade guardrails (dollar risk, ATR/time stops, trailing/take-profit), session/day/week breakers, VaR/ES budgets, cost/venue gates.
- **Lean controls**
  - Manual: manage stop levels and kill switches in `OnData` or scheduled events (`Schedule.On`).
  - Framework: `SetRiskManagementModel` with built-in modules (`TrailingStopRiskManagementModel`, `MaximumDrawdownPercentPerSecurity`, etc.) or custom `RiskManagementModel` returning reduced target positions.
  - `SetBrokerageModel` influences margin requirements and buying power.
- **Key details**
  - Track realized/unrealized P&L per symbol and liquidity metrics (ADV/book depth).
  - Monitor order rejects via `OnOrderEvent` and enforce venue-specific risk rules.
  - Implement kill-switches with `Liquidate` and `Quit` for emergency stops.

---

## 6. Execution & Order Management

- **Scope**: converting targets into orders (TWAP/VWAP/POV schedulers, slicing, routing, limit/post-only vs IOC), slippage/impact modeling, idempotency and reconciliation, latency/throttles.
- **Lean controls**
  - Direct order API: `MarketOrder`, `LimitOrder`, `StopMarketOrder`, `StopLimitOrder`, `OrderDuration` (GTC/Day), `OrderTicket` modification (`UpdateOrderFields`).
  - Framework execution models (`SetExecution`) like `ImmediateExecutionModel`, `VolumeWeightedAveragePriceExecutionModel`, or custom `ExecutionModel` generating child orders from Insights.
  - Smart order routing via brokerage models (depends on connected broker/exchange) and custom logic that submits to specified markets.
- **Key details**
  - Maintain custom order IDs and map Lean ticket IDs to venue IDs.
  - Throttle submissions with `TimeRules`, counters, or schedulers to avoid duplication.
  - Monitor fill progress through `ExecutionModel` outputs and order events.

---

## 7. Post-Trade Analytics & Feedback Loop

- **Scope**: P&L accounting (realized/unrealized, fees/funding/borrow), benchmarking (VWAP, IS), risk stats (drawdown, expectancy, VaR/ES), compliance logs, learning loop (drift detection, parameter updates).
- **Lean controls**
  - `Portfolio` class exposes holdings, average price, fees, unrealized P&L; `TradeBuilder` summarises trades.
  - `OnEndOfAlgorithm`, `OnOrderEvent`, `OnEndOfDay` provide hooks for logging metrics and exporting JSON/CSV.
  - Custom statistics via `SetRuntimeStatistic` and `self.Debug`/`self.Log`.
- **Key details**
  - Maintain immutable logs of signal inputs/outputs, order intents, fills, and state transitions.
  - Compute benchmark comparisons using custom data sources.
  - Route metrics to external dashboards via API calls or file outputs for continuous feedback.

---

## 8. Research & Validation Infrastructure

- **Scope**: backtesting realism (latency, fill modeling, borrow/funding costs, partial fills), robustness checks (walk-forward, bootstrap, Monte Carlo), stress/scenario testing, model governance (versioning, approvals, rollbacks).
- **Lean controls**
  - Lean CLI/Engine supports backtests and optimizations; config through `config.json`.
  - `SetExecution`, `SetFillModel`, `SetSlippageModel`, `SetFeeModel`, `SetLeverage` allow scenario-specific modeling.
  - Walk-forward/backtest automation via Research notebooks + Lean `BacktestResult` JSON for analytics.
- **Key details**
  - Record parameter grids, seeds, and sample periods for reproducibility.
  - Maintain model registries via metadata files or external databases.
  - Document dataset versions and automate Lean CLI runs for replication.

---

## 9. Monitoring, Operations & Governance

- **Scope**: runtime health (feed liveness, latency, CPU/memory), P&L/exposure dashboards, alerting, kill-switch automation, secrets/config management, compliance/audit logging.
- **Lean controls**
  - Runtime statistics & charts (`SetRuntimeStatistic`, `Plot`) for dashboards.
  - `Schedule.On` for periodic health checks and risk resets.
  - Deployment pipelines: Lean CLI + QuantConnect Cloud manage config-as-code, environment separation, API keys.
  - Logging: `Debug`, `Log`, `Error` streams, order/portfolio events recorded automatically in backtest/live logs.
- **Key details**
  - Maintain immutable audit logs (signals → orders → fills) and config versioning.
  - Handle secrets via Lean Cloud or environment variables.
  - Define kill-switch triggers (`Liquidate`, trading disable) and runbooks for incidents.

---

## 10. Crypto-Specific Considerations

- **Scope**: perpetual funding, ADL/clawback risk, liquidation engines, oracle dependencies, spot/perp basis hedging, custody/transfer procedures.
- **Lean controls**
  - Crypto universes via `AddCrypto`, `AddCryptoFuture`, `SetBrokerageModel(BrokerageName)`, and brokerage settings for margin/funding rules.
  - Funding rates/borrow costs modeled through custom fee models (`SetFeeModel`) or manual adjustments in P&L calculations.
  - Multi-venue hedging by adding multiple symbols and managing cross-exchange positions.
- **Key details**
  - Handle lot sizes, minimum notionals, and cross-venue leverage rules.
  - Incorporate funding/borrow costs into sizing and P&L.
  - Document custody/transfer workflows and provide oracle/price-feed redundancy.

---

## Directory Expectations (Lean-centric)

| Path | Role |
|------|------|
| `main.py` | Houses Lean algorithm with explicit components: data adapters, feature engine, signal model, allocator, risk guard, execution planner, OMS hooks, post-trade logger. |
| `research/notebooks/` | Research environment to prototype each component; must document Lean-specific interfaces (e.g., how a feature maps to `IndicatorBase`). |
| `research/scripts/` | Promote reusable loaders, feature builders, signal modules, allocators, risk/exec utilities so Lean can import them. |
| `docs/specs/` & `docs/runbooks/` | Written specs for each component (data layer, signals, risk controls, execution, ops) plus operational playbooks. |
| `research/research_log.md` | Evidence log tying research artifacts to Lean implementation details (symbol universe, indicator settings, parameter hashes, approval status). |

Keep this document authoritative: whenever you refine a component or learn a Lean-specific constraint, update the relevant section so research and engineering stay aligned.
