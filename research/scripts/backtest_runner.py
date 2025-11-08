# region imports
from AlgorithmImports import *
# endregion
"""
Lean/QuantConnect backtest runner scaffold.

Goal: provide a single entry point for parameterized backtests both locally (`lean backtest`)
and in QuantConnect Cloud (`lean cloud backtest` or API calls). For now we just capture intent.
"""

from pathlib import Path
from typing import Dict, Any


def build_command(config_path: Path, overrides: Dict[str, Any] | None = None) -> list[str]:
    """
    Return the CLI command that would run a backtest.
    This stub only assembles arguments; execution will be added later.
    """

    cmd = ["lean", "cloud", "backtest", str(config_path)]
    if overrides:
        for key, value in overrides.items():
            cmd += ["--parameter", f"{key}={value}"]
    return cmd


# TODO: add functions to invoke the command, poll for completion, and archive results/metadata.
