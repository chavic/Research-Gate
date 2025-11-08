# Execution & OMS Specification

## Purpose
Provide the blueprint for converting target deltas into venue-aware child orders while controlling slippage, impact, and operational risk.

## Components
- **Schedulers**: TWAP, VWAP, POV, Implementation Shortfall, urgency decays.
- **Order types**: market, limit/post-only, IOC/FOK, pegged, iceberg; Lean order APIs to use.
- **Routing**: venue preference logic, dark/alternative venues, broker algos, retry behavior.
- **Safety**: idempotent client order IDs, duplicate suppression, reject handling, pacing/throttle rules.

## Interfaces
- `research/scripts/execution.py` – planners should accept target quantities + context (liquidity, spreads, urgency) and emit child-order plans.
- Lean: either integrate via `ExecutionModel` in the framework or custom logic calling `OrderTicket` methods with plan outputs.
- Monitoring: all OMS decisions must be logged and surface metrics for TCA.

## TODO
- Define data structures for child orders (already stubbed as `ChildOrder`); add fields for venue, limit price, participation cap.
- Document fallback plan if primary venue fails.
- Specify how schedulers pull real-time liquidity inputs (levels, ADV, queue depth).
