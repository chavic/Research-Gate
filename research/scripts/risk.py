# region imports
from AlgorithmImports import *
# endregion
"""
Risk guard scaffolding.

Use this module to implement reusable VaR/ES calculators, drawdown breakers, cost gates, and
Lean-compatible `RiskManagementModel` helpers.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class RiskState:
    """Tracks exposure, P&L, and breaker status for downstream components."""

    pnl: float = 0.0
    exposure: Dict[str, float] | None = None
    breakers_triggered: bool = False


class RiskGuard:
    """Placeholder base class for risk overlays."""

    def evaluate(self, targets: Dict[str, float], context: Dict[str, float]) -> Dict[str, float]:
        """
        Return clipped targets that satisfy risk constraints.
        Override this in concrete guards (ATR stops, VaR caps, etc.).
        """

        return targets


class TrailingStopGuard(RiskGuard):
    """Example stub showing how guards might be structured."""

    def __init__(self, stop_pct: float = 0.03) -> None:
        self.stop_pct = stop_pct

    def evaluate(self, targets: Dict[str, float], context: Dict[str, float]) -> Dict[str, float]:
        # TODO: incorporate price history and realized P&L.
        return super().evaluate(targets, context)
