"""
Signal module namespace.

Drop deterministic rules, ML inference wrappers, and ensemble utilities here.
Expose a registry or factory functions so Lean algorithms can import signals by name.
"""

from typing import Protocol, Any


class SignalModel(Protocol):
    """Protocol describing the interface signal implementations should follow."""

    def score(self, features: dict[str, Any]) -> tuple[float, float]:
        """
        Convert feature dictionary into an (edge, confidence) tuple.
        Replace with richer contracts as research matures.
        """

    # TODO: add state reset hooks, serialization helpers, etc.
