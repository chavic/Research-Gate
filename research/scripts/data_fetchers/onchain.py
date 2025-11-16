# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Literal

import pandas as pd

from . import utils

GLASSNODE_ENDPOINT = "https://api.glassnode.com/v1/metrics"
DEFAULT_METRICS: dict[str, str] = {
    "active_addresses": "addresses/active_count",
    "exchange_netflow": "distribution/exchange_net_position_change",
    "whale_tx_usd": "transactions/transfers_volume_exchanges",
}


def _fetch_metric(
    metric: str,
    symbol: str,
    start: datetime,
    end: datetime,
    api_key: str,
    interval: Literal["24h", "1h"] = "24h",
    limiter: utils.RateLimiter | None = None,
) -> pd.DataFrame:
    params = {
        "a": symbol.upper(),
        "s": int(start.timestamp()),
        "u": int(end.timestamp()),
        "i": interval,
        "api_key": api_key,
    }
    if limiter:
        limiter.wait()
    data = utils.json_request(f"{GLASSNODE_ENDPOINT}/{metric}", params=params)
    frame = pd.DataFrame(data)
    if frame.empty:
        return frame
    if "t" in frame.columns:
        frame["timestamp"] = pd.to_datetime(frame["t"], unit="s", utc=True)
        frame = frame.drop(columns=["t"])
    frame = frame.set_index("timestamp").sort_index()
    frame = frame.rename(columns={"v": metric.split("/")[-1]})
    frame.columns = [metric]
    return frame


def run_pipeline(
    symbols: Iterable[str],
    out_dir: Path,
    metrics: dict[str, str] | None = None,
    interval: Literal["24h", "1h"] = "24h",
    overwrite: bool = False,
    lookback: timedelta = timedelta(days=365),
) -> dict[str, Path]:
    """
    Download on-chain metrics from Glassnode (free tier) for each symbol.

    Parameters
    ----------
    symbols : iterable of str
        Assets (e.g., "BTC", "ETH").
    out_dir : Path
        Directory where `<symbol>_onchain.parquet` files are stored.
    metrics : mapping
        Dictionary of column -> Glassnode metric endpoint.
    interval : {"24h", "1h"}
        Sampling interval supported by Glassnode.
    overwrite : bool
        If False and a file already exists, skip downloading.
    lookback : timedelta
        Time window to request when overwriting or when no cache exists.
    """

    api_key = utils.env_or_raise("GLASSNODE_API_KEY")
    metrics = metrics or DEFAULT_METRICS
    limiter = utils.RateLimiter(calls=10, period=60)  # per Glassnode free tier limits
    utils.ensure_directory(out_dir)

    output_files: dict[str, Path] = {}
    end = datetime.now(tz=timezone.utc)
    start = end - lookback

    for symbol in symbols:
        out_file = out_dir / f"{symbol.lower()}_onchain.parquet"
        if out_file.exists() and not overwrite:
            output_files[symbol] = out_file
            continue

        frames: list[pd.DataFrame] = []
        for column, endpoint in metrics.items():
            frame = _fetch_metric(endpoint, symbol, start, end, api_key, interval, limiter=limiter)
            if not frame.empty:
                frame = frame.rename(columns={endpoint: column})
            frames.append(frame)

        combined = utils.merge_frames(frames)
        if combined.empty:
            continue
        utils.write_time_series(combined, out_file)
        output_files[symbol] = out_file

    return output_files

