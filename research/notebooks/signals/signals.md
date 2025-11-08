# Signals Notebook Hub

## Notebooks
- `idea_bank_signals.ipynb` – catalog of momentum, volatility, order-book, seasonality, ML, and behavioral signals.
- `idea_bank_Indicators_signals.ipynb` – end-to-end BTC indicator pipeline (data prep, implementation, backtests, visuals).

## Sub-Hubs
- `ai/` – reasoning/ML-driven alpha experiments (`idea_bank_ai_r1.ipynb`, `idea_bank_hrm.ipynb`) plus `ai.md` workflow notes.
- `combinations/` – ensemble orchestration notebooks and docs (see `combinations/combinations.md`).
- `legacy/` – historical drafts retained for reference; treat them as read-only artifacts.

## How to Use
1. Run shared loaders/backtests from `research/scripts/` to keep notebooks clean.
2. Log key discoveries in `research/research_log.md` once runs finish.
3. When a signal is production-ready, note the code path that should move into LEAN algorithms.

## Open Threads
- Tag new notebooks here as you branch into niche signal families.
- Cross-link any datasets or cached outputs required for reproducibility.
