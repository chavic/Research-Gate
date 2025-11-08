"""
Crypto-specific utilities.

Implement funding-rate estimators, basis calculators, and custody/reconciliation helpers here.
Keep venue-specific quirks isolated so the rest of the stack can stay venue-agnostic.
"""

from dataclasses import dataclass


@dataclass
class FundingSnapshot:
    symbol: str
    rate: float
    timestamp: str


def annualize_funding(rate: float, periods_per_year: int = 365) -> float:
    """Simple helper for extrapolating perp funding rates."""

    return (1 + rate) ** periods_per_year - 1


# TODO: add basis spread calculators, ADL risk estimators, custody reconciliation workflows.
