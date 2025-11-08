# Post-Trade & Feedback Notebook Hub

## Mission
Measure realized performance (P&L, fees, funding, borrow), benchmark slippage, attribute risk/return, and feed the insights back into research, risk, and execution loops.

## Initial Notebook Targets
- `tca_dashboard.ipynb` – VWAP/TWAP/arrival benchmarks, slippage decomposition, and execution quality metrics.
- `attribution.ipynb` – contributions by signal, venue, time bucket, factor exposure, and regime.
- `compliance_reporting.ipynb` – immutable logs, surveillance checks, and report templates for audit.

## Research Checklist
- Extract trade/fill data from Lean backtests or live runs (`OnOrderEvent`, `TradeBuilder`) and store reproducible datasets.
- Define runtime statistics and reporting cadences (intra-day vs daily) that align with monitoring requirements.
- Export reusable analytics helpers to `research/scripts/reporting.py` so production code can call the same TCA logic.
