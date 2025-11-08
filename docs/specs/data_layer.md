# Data Layer Specification

## Purpose
Define how we request, normalize, and store market data so research notebooks, Lean backtests, and live deployments consume the exact same input contract.

## Key Decisions
- **Source**: QuantConnect data feeds (crypto/equity/forex/futures) via `AddSecurity` and `History`.
- **Parameters to log**: symbol, market, security type, resolution, start/end, fill-forward, data normalization mode, extended hours flag, brokerage model, fee/slippage model IDs, consolidator settings.
- **Quality controls**: missing data detection, duplicate suppression, clock skew checks, corporate action/funding adjustments.
- **Replay/export**: when persisting fixtures, store raw rows plus the `DataRequestSpec` (see `research/scripts/data_loader.py`) so pulls remain reproducible.

## Interfaces
- `research/scripts/data_loader.py` – registers each data request and (eventually) fetches/validates it.
- Lean `Initialize` – must call `SetTimeZone`, `SetSecurityInitializer`, `AddCrypto/...` using the same parameters recorded by the data loader.
- Notebook templates – load the logged specs to ensure offline analysis uses the identical query contract.

## TODO
- Define schema for persisted request logs (JSON/YAML).
- Decide on storage format for replay buffers (Parquet vs Feather) and retention policy.
- Document gap-handling strategy (forward-fill, interpolation, quarantine).
