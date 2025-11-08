# Post-Trade Analysis Runbook

## Objective
Ensure daily P&L, slippage, and attribution metrics are produced consistently and deviations trigger follow-up research.

## Daily Checklist
1. Export fills/orders from Lean backtest/live logs or brokerage (CSV/JSON).
2. Run `research/scripts/reporting.py` helpers (or equivalent notebook) to compute:
   - Realized vs unrealized P&L
   - VWAP/TWAP/arrival slippage
   - Fees, funding, borrow costs
   - Attribution by signal, venue, and time bucket
3. Compare metrics against expected bands; log anomalies in the research log.

## Escalation
- If slippage exceeds budget, loop execution researchers to inspect liquidity assumptions.
- If P&L diverges from model expectations, check signals, allocator, and risk overrides.
- Always archive reports (PDF/HTML/JSON) with timestamps for audit.
