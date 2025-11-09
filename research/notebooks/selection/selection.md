# Asset Selection Notebook Hub

## Mission

Identify, score, and prioritize assets demonstrating breakout characteristics across price action, liquidity, and on-chain participation so we can deploy capital into the strongest momentum cohorts with controlled drawdowns.

## Initial Notebook Targets

- `selection_playbook.ipynb` – curate factor blends (price acceleration, relative volume, whale activity) and define tiered ranking frameworks.
- `selection_booming_assets.ipynb` – prototype the “booming asset” detection workflow leveraging QuantConnect datasets, CoinGecko market caps, and social/on-chain signals.
- `selection_risk_controls.ipynb` – stress-test selection lists for liquidity, slippage, and macro overlays before handing them to portfolio construction.

## Research Checklist

- Stand up QuantConnect Research scaffolding (QuantBook, data request registry, sample history pulls) before prototyping.
- Document feature provenance and normalization logic for every selection factor in `research/scripts`.
- Produce walk-forward backtests covering both bullish and stressed markets; include breakdowns by asset class and exchange venue.
- Capture model diagnostics (precision/recall on breakout labels, turnover, hit rate) and attach plots/notebooks to the research log.
- Promote validated selection pipelines into reusable modules shared with signal generation and portfolio construction teams.
