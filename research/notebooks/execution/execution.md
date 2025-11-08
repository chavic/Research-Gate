# Execution & OMS Notebook Hub

## Mission
Design schedulers, routing heuristics, and OMS safety rails that convert target deltas into efficient, venue-aware child orders under Lean’s execution framework.

## Initial Notebook Targets
- `scheduler_lab.ipynb` – TWAP/VWAP/POV/IS comparisons with urgency decay models.
- `impact_modeling.ipynb` – slippage/impact curve estimation and calibration against historical fills.
- `router_design.ipynb` – venue selection logic, dark/peg strategies, and throttling tests.

## Research Checklist
- Capture how Lean order types (`MarketOrder`, `LimitOrder`, `OrderTicket` updates) map to each scheduler tactic.
- Define idempotency, retry, and kill-switch behavior for OMS workflows and ensure logs include client order IDs.
- Promote reusable planners/routers into `research/scripts/execution.py`, leaving notebooks for analysis and visualization.
