# Checkpoint: Research Gate Modular BTC v0

- **Date**: 2025-11-09
- **Backtest**: [Dancing Fluorescent Pink Mule](https://www.quantconnect.com/project/25070614/0b188dabdbd72ddc9c459495f424db04)
- **Project**: Research Gate (ID 25070614)

## Snapshot

- Start capital: $100,000 (Kraken cash account)
- Strategy: Randomized long-only BTC with modular contracts (data adapter, feature engine, signal model, allocator, trailing-stop risk guard, execution planner) + tiered fee model (Kraken/Binance ready)
- Venue parameter: `exchange_venue=kraken`
- Positioning: 95% allocation on entries, 3% trailing stop, 5-minute cooldown

## Key Metrics

| Metric | Value |
|--------|-------|
| End Equity | $5,357,613 |
| Net Profit | 5,257.6% |
| Sharpe | 66.86 |
| Sortino | 342.85 |
| Max Drawdown | 17.0% |
| Total Orders | 251 |
| Fees Paid | $762,869 |
| Win Rate | 70% |
| Avg Win / Loss | +5.59% / -1.72% |
| Portfolio Turnover | 63.5% |

## Notes

- Performance remains unrealistically high because the placeholder signal keeps the portfolio long most of the year with tight trailing stops; fees alone are not enough to normalize results.
- Cost model verified: Kraken tiered taker fees applied (0.26% baseline) resulting in ~$763k total fees.
- This checkpoint captures the first end-to-end modular pipeline (data → execution) ready for future signals/allocators.

## Next Actions

1. Replace the random signal with research-derived models (momentum, mean-reversion, AI, etc.).
2. Add realistic slippage/fill modelling and stricter risk controls.
3. Populate research notebooks & scripts with production-ready code and log experiments.
