# region imports
from AlgorithmImports import *
# endregion
"""
Utilities for downloading external datasets into the local `data/` cache.

Each submodule exposes a `run_pipeline(...)` entry point that downloads data
from free-tier APIs when possible, respecting rate limits and skipping work
if the corresponding cache files already exist.
"""

from . import onchain, funding, sentiment, defi, tokenomics, execution  # noqa: F401

__all__ = [
    "onchain",
    "funding",
    "sentiment",
    "defi",
    "tokenomics",
    "execution",
]





