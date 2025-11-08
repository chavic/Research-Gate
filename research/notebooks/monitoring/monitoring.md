# Monitoring & Ops Notebook Hub

## Mission
Instrument strategy health—data feed liveness, latency, resource usage, P&L exposure, alerts, and kill-switch behavior—to keep Lean deployments safe.

## Initial Notebook Targets
- `health_dashboard.ipynb` – visualize tick-to-trade latency, backlog depth, heartbeat gaps, CPU/NIC metrics.
- `alert_rules.ipynb` – prototype SLO thresholds for P&L drawdowns, limit breaches, data gaps, or reject storms.
- `kill_switch_sim.ipynb` – simulate breaker triggers and verify flatten/disable workflows.

## Research Checklist
- Define telemetry sources (Lean runtime statistics, external metrics, broker APIs) and how they map into dashboards.
- Document alert routing/escalation paths and auto-remediation scripts.
- Export monitoring utilities to `research/scripts/monitoring.py` or ops tooling so live systems can reuse them.
