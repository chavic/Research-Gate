# Kill-Switch Runbook

## Triggers
- Intraday drawdown exceeds predefined threshold.
- VaR/ES estimates breach allocated risk budget.
- Execution rejects exceed tolerance or venue health flags critical.
- Data/monitoring detects stale or missing feeds beyond tolerance.

## Immediate Actions
1. Call `Liquidate()` on all active symbols (or send bulk close orders via broker if running live outside Lean).
2. Disable new signal generation/allocations by setting a global `halt` flag.
3. Notify stakeholders (Slack/Email/Phone) with timestamp, breach reason, and current exposure.

## Post-Event Steps
- Capture logs, market data snapshots, and risk state for forensics.
- Open incident entry referencing `research/research_log.md`.
- Run diagnostic notebooks (risk, execution, data) to identify root cause before re-enabling trading.
