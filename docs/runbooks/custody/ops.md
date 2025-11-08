# Crypto Custody & Ops Runbook

## Scope
Document wallet operations, withdrawal/transfer procedures, and exchange reconciliation steps for digital-asset strategies.

## Wallet Management
- Maintain hot vs cold wallet addresses and associated keys in a secure secrets store.
- Schedule regular small-value test withdrawals to ensure exchange connectivity.
- Log every deposit/withdrawal with transaction hash, confirmations, and custody reviewer.

## Exchange Reconciliation
- Daily: reconcile Lean/Broker positions with on-chain balances and exchange statements.
- Track funding rate accruals, borrow fees, and basis trades across venues.
- Flag discrepancies > threshold for manual investigation before next trading session.

## Incident Handling
- In case of withdrawal delays or chain congestion, throttle trading size and notify stakeholders.
- For suspected compromise, rotate keys, pause trading, and follow incident response plan.

## TODO
- Fill in venue-specific instructions (Kraken, Binance, etc.) once accounts are finalized.
- Link to secrets management SOP describing how API keys are provisioned.
