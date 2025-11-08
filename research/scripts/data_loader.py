# region imports
from AlgorithmImports import *
# endregion
"""
Data loader scaffolding.

Responsibilities:
- Define the canonical schema for QuantConnect history/stream requests.
- Record query parameters (symbol, market, resolution, fill-forward mode, normalization, start/end) for reproducibility.
- Provide hook methods (to be implemented later) for fetching data, running integrity checks, and exporting replay sets.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DataRequestSpec:
    """Immutable description of a QuantConnect data pull."""

    symbol: str
    market: str
    security_type: str
    resolution: str
    start: str
    end: str
    fill_forward: bool = True
    normalization_mode: str = "Adjusted"
    extended_hours: bool = False
    additional_params: Optional[Dict[str, Any]] = None


class DataLoader:
    """Placeholder adapter that will wrap QC History/API calls."""

    def __init__(self) -> None:
        self._requests: list[DataRequestSpec] = []

    def register(self, spec: DataRequestSpec) -> None:
        """Store a request spec so we can reproduce dataset pulls later."""

        self._requests.append(spec)

    def list_requests(self) -> list[DataRequestSpec]:
        """Return all registered specs (no network calls yet)."""

        return list(self._requests)

    # TODO: add fetch/history/export methods once data work begins.
