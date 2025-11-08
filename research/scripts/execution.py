# region imports
from AlgorithmImports import *
# endregion
"""
Execution planner scaffolding.

Provide schedulers (TWAP/VWAP/POV), child-order slicers, and routing heuristics that both research
notebooks and Lean algorithms can call.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ChildOrder:
    """Represents a planned child order before submission."""

    symbol: str
    quantity: float
    price: float | None
    order_type: str
    eta: str  # ISO8601 timestamp string placeholder


class ExecutionPlanner:
    """Base class for execution strategies."""

    def plan(self, targets: Dict[str, float], context: Dict[str, float]) -> List[ChildOrder]:
        raise NotImplementedError


class ImmediatePlanner(ExecutionPlanner):
    """Placeholder planner that just emits a single market-style child order."""

    def plan(self, targets: Dict[str, float], context: Dict[str, float]) -> List[ChildOrder]:
        orders: List[ChildOrder] = []
        for symbol, qty in targets.items():
            orders.append(
                ChildOrder(
                    symbol=symbol,
                    quantity=qty,
                    price=None,
                    order_type="MARKET",
                    eta=context.get("timestamp", "T+0"),
                )
            )
        return orders

    # TODO: add TWAP/VWAP/POV planners with liquidity/impact inputs.
