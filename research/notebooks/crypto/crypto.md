# Crypto Research Hub

## Mission
Capture venue-specific behavior for digital assets—perpetual funding, basis trades, custody, and exchange microstructure—so Lean strategies can price, hedge, and operate safely across spot and derivative venues.

## Structure
- `microstructure/` – order-book research split into `current/` (active notebooks) and `legacy/` (historical drafts). Use these notebooks to document queue models, latency assumptions, and venue quirks.
- Future sub-folders can cover `perpetuals/`, `basis/`, `custody/`, etc., each with their own notebook hubs and legacy archives.

## Research Checklist
- Map every notebook to specific Lean settings (brokerage model, margin rules, funding calculations) and record any venue-specific API requirements.
- Track oracle dependencies, settlement schedules, and withdrawal/custody playbooks for each exchange studied.
- Feed validated components (funding calculators, basis hedgers) into `research/scripts/crypto/` modules for reuse in production algorithms.
