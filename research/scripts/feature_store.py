"""
Feature store scaffolding.

Use this module to register feature definitions, track metadata (windows, decay, null handling),
and provide helper functions for parity testing between research and live Lean environments.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any


@dataclass(frozen=True)
class FeatureSpec:
    """Describes a single feature and how it should be computed."""

    name: str
    inputs: tuple[str, ...]
    window: int
    description: str
    version: str = "v0"
    params: Dict[str, Any] | None = None


class FeatureRegistry:
    """Lightweight registry storing feature specs and callable builders."""

    def __init__(self) -> None:
        self._specs: Dict[str, FeatureSpec] = {}
        self._builders: Dict[str, Callable[..., Any]] = {}

    def register(self, spec: FeatureSpec, builder: Callable[..., Any]) -> None:
        """Register a feature spec + builder callable."""

        self._specs[spec.name] = spec
        self._builders[spec.name] = builder

    def describe(self, name: str) -> FeatureSpec:
        """Return metadata for a feature."""

        return self._specs[name]

    def builder(self, name: str) -> Callable[..., Any]:
        """Return the callable used to compute the feature."""

        return self._builders[name]

    # TODO: add parity-testing helpers and serialization for registry snapshots.
