# region imports
from AlgorithmImports import *
# endregion

from pathlib import Path
from typing import Iterable

import pandas as pd

from . import utils

DEFILLAMA_UNLOCKS_URL = (
    "https://raw.githubusercontent.com/DefiLlama/token-unlocks/master/{symbol}.json"
)


def _fetch_defillama(symbol: str) -> pd.DataFrame:
    url = DEFILLAMA_UNLOCKS_URL.format(symbol=symbol.lower())
    try:
        payload = utils.json_request(url)
    except Exception:
        return pd.DataFrame()

    events = payload.get("schedule", [])
    if not events:
        return pd.DataFrame()

    records = []
    for event in events:
        ts = event.get("timestamp") or event.get("date")
        if ts is None:
            continue
        records.append(
            {
                "event_time": pd.to_datetime(ts, utc=True),
                "event": event.get("type") or event.get("title", "unlock"),
                "amount": float(event.get("amount", 0)),
                "amount_usd": float(event.get("amountUSD", 0)),
                "category": event.get("category"),
                "notes": event.get("notes"),
            }
        )

    frame = pd.DataFrame(records)
    if frame.empty:
        return frame
    return frame.sort_values("event_time")


def run_pipeline(
    symbols: Iterable[str],
    out_dir: Path,
    overwrite: bool = False,
) -> dict[str, Path]:
    """
    Download token unlock schedules from the DefiLlama open dataset.

    Parameters
    ----------
    symbols : iterable of str
        Token symbols (e.g., "APT", "ARB"). Availability depends on dataset.
    out_dir : Path
        Directory for `<symbol>_events.parquet`.
    """

    utils.ensure_directory(out_dir)
    output_files: dict[str, Path] = {}

    for symbol in symbols:
        out_file = out_dir / f"{symbol.lower()}_events.parquet"
        if out_file.exists() and not overwrite:
            output_files[symbol] = out_file
            continue

        frame = _fetch_defillama(symbol)
        if frame.empty:
            continue
        utils.write_time_series(frame.set_index("event_time"), out_file)
        output_files[symbol] = out_file

    return output_files
