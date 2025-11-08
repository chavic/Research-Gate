# Operations & Monitoring Runbook

## Scope
Defines how we monitor strategy health in Lean live trading, which metrics trigger alerts, and what responders must do when thresholds are breached.

## Key Metrics
- Tick-to-trade latency, message backlog depth, missed bar count.
- P&L (realized/unrealized), exposure by asset, VaR/ES vs budget.
- Data feed health (heartbeat gaps, clock skew), order reject rates, brokerage connectivity.

## Alert Thresholds (draft)
- **Latency**: >2× baseline for 3 consecutive minutes.
- **Drawdown**: intraday loss > X% of capital or > Y standard deviations from plan.
- **Reject storm**: >5 rejects in 1 minute or >10 bps slippage vs model.
- **Data gap**: no ticks/bars for 2× expected interval.

## Procedures
1. Alerts route to on-call channel with run ID, metrics, and recommended action.
2. Operator reviews Lean logs + monitoring dashboards, confirms issue.
3. If breaker criteria met, execute kill-switch (call `Liquidate`, disable scheduling, notify broker).
4. File incident report referencing `research/research_log.md` entry for audit.

## TODO
- Populate actual thresholds per strategy.
- Automate alert dispatch (PagerDuty/Slack) once monitoring scripts integrate with telemetry.
- Add post-incident checklist and recovery playbook.
