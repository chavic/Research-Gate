# Risk Controls Specification

## Purpose
Detail the guardrails that sit between portfolio targets and order generation so no order leaves the system unless post-trade exposure stays within limits.

## Control Layers
- **Per-trade**: max dollar-at-risk, ATR/time stops, trailing/take-profit rules, borrow/liq caps.
- **Session/Day/Week**: loss breakers, VaR/ES budgets, exposure ladders, position-count limits.
- **Cost gates**: spread/slippage ceilings, fee/funding thresholds, ADV participation limits.
- **Venue safety**: reject storm detection, latency throttles, margin buffers, venue health signals.

## Implementation Hooks
- `research/scripts/risk.py` – houses reusable guard logic (VaR calculators, breaker state machines).
- Lean: use `SetRiskManagementModel` for framework algos or call guard objects inside `OnData` before orders.
- Monitoring: tie breaker events into alerting/kill-switch procedures documented in runbooks.

## TODO
- Enumerate exact limits per strategy (e.g., BTC max exposure, drawdown triggers).
- Define stress scenarios feeding into VaR/ES estimates.
- Document how guard decisions are logged/audited.
