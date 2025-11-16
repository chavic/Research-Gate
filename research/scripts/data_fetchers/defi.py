# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from . import utils

DEFILLAMA_PROTOCOL_URL = "https://api.llama.fi/protocol"
DEFILLAMA_BORROW_URL = "https://yields.llama.fi/pools"


def _fetch_tvl(protocol: str) -> pd.DataFrame:
    data = utils.json_request(f"{DEFILLAMA_PROTOCOL_URL}/{protocol}")
    chain_tvls = data.get("chainTvls", {})
    frames: list[pd.DataFrame] = []
    for key, series in chain_tvls.items():
        df = pd.DataFrame(series)
        if df.empty:
            continue
        df["timestamp"] = pd.to_datetime(df["date"], unit="s", utc=True)
        df = df.set_index("timestamp")
        df = df.rename(columns={"totalLiquidityUSD": f"tvl_usd_{key.lower()}"})
        frames.append(df[[f"tvl_usd_{key.lower()}"]])
    return utils.merge_frames(frames)


def _fetch_rates(symbol: str) -> pd.DataFrame:
    data = utils.json_request(DEFILLAMA_BORROW_URL)
    rows = data.get("data", [])
    filtered = [
        row
        for row in rows
        if row.get("symbol", "").upper() == symbol.upper() and row.get("apyType") in {"borrow", "supply"}
    ]
    if not filtered:
        return pd.DataFrame()

    records = []
    for row in filtered:
        records.append(
            {
                "timestamp": pd.to_datetime(row["timestamp"], unit="s", utc=True),
                "pool": row.get("project"),
                "apy": row.get("apy"),
                "type": row.get("apyType"),
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        return df
    pivot = (
        df.pivot_table(index="timestamp", columns="type", values="apy", aggfunc="mean")
        .rename(columns={"borrow": "borrow_rate", "supply": "supply_rate"})
        .sort_index()
    )
    return pivot


def run_pipeline(
    symbols: Iterable[str],
    protocol_map: dict[str, str],
    out_dir: Path,
    overwrite: bool = False,
    lookback: timedelta = timedelta(days=365),
) -> dict[str, Path]:
    """
    Combine DefiLlama TVL history with average borrow/supply rates.

    Parameters
    ----------
    symbols : iterable of str
        Tokens of interest (e.g., "ETH").
    protocol_map : dict
        Mapping of symbol -> DefiLlama protocol slug.
    out_dir : Path
        Directory for `<symbol>_defi.parquet`.
    """

    utils.ensure_directory(out_dir)
    output_files: dict[str, Path] = {}
    cutoff = datetime.now(tz=timezone.utc) - lookback

    for symbol in symbols:
        out_file = out_dir / f"{symbol.lower()}_defi.parquet"
        if out_file.exists() and not overwrite:
            output_files[symbol] = out_file
            continue

        protocol = protocol_map.get(symbol.upper())
        frames: list[pd.DataFrame] = []
        if protocol:
            tvl = _fetch_tvl(protocol)
            if not tvl.empty:
                frames.append(tvl)
        rates = _fetch_rates(symbol)
        if not rates.empty:
            frames.append(rates / 100.0)  # convert to decimal rates

        combined = utils.merge_frames(frames)
        if combined.empty:
            continue
        combined = combined[combined.index >= cutoff]
        utils.write_time_series(combined, out_file)
        output_files[symbol] = out_file

    return output_files





