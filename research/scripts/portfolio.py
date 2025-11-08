"""
Allocator scaffolding.

Contains base classes for turning signal outputs into target weights/quantities while respecting
volatility budgets, leverage caps, and other constraints.
"""

from dataclasses import dataclass
from typing import Protocol, Dict


@dataclass
class AllocationResult:
    """Target weights keyed by symbol."""

    weights: Dict[str, float]
    notes: str = ""


class Allocator(Protocol):
    """Allocator contract shared between research notebooks and Lean."""

    def compute(self, scores: Dict[str, float], context: Dict[str, float]) -> AllocationResult:
        """
        Convert signals into portfolio weights.
        `context` can include volatility estimates, covariance entries, cash, etc.
        """


class FixedFractionAllocator:
    """Example allocator stub; fill in logic when sizing research begins."""

    def __init__(self, fraction: float = 0.95) -> None:
        self.fraction = fraction

    def compute(self, scores: Dict[str, float], context: Dict[str, float]) -> AllocationResult:
        # TODO: replace placeholder with volatility targeting / constraint logic.
        if not scores:
            return AllocationResult(weights={})

        symbol, score = max(scores.items(), key=lambda kv: kv[1])
        weight = self.fraction if score > 0 else 0.0
        return AllocationResult(weights={symbol: weight}, notes="Fixed fraction placeholder")
