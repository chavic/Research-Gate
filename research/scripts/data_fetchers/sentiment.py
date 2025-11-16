# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from . import utils

LUNARCRUSH_URL = "https://api.lunarcrush.com/v2"


def _fetch_timeseries(
    symbol: str,
    start: datetime,
    end: datetime,
    api_key: str,
    interval: str = "day",
) -> pd.DataFrame:
    params = {
        "symbol": symbol.upper(),
        "data_points": int((end - start).days) + 2,
        "interval": interval,
        "data": "assets",
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
    }
    limiter = utils.RateLimiter(calls=30, period=60)
    limiter.wait()
    data = utils.json_request(
        f"{LUNARCRUSH_URL}?key={api_key}",
        params=params,
    )
    rows = data.get("data", [])
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
    frame = frame.set_index("timestamp").sort_index()
    desired = {
        "social_dominance": "social_dominance_score",
        "sentiment_score": "galaxy_score",
        "mention_velocity": "social_volume",
    }
    existing = {col: frame[val] for col, val in desired.items() if val in frame.columns}
    return pd.DataFrame(existing)


def run_pipeline(
    symbols: Iterable[str],
    out_dir: Path,
    overwrite: bool = False,
    lookback: timedelta = timedelta(days=180),
    interval: str = "day",
) -> dict[str, Path]:
    """
    Download community sentiment metrics from the LunarCrush free API.

    Requires the environment variable `LUNARCRUSH_API_KEY`.
    """

    api_key = utils.env_or_raise("LUNARCRUSH_API_KEY")
    utils.ensure_directory(out_dir)
    output_files: dict[str, Path] = {}
    end = datetime.now(tz=timezone.utc)
    start = end - lookback

    for symbol in symbols:
        out_file = out_dir / f"{symbol.lower()}_sentiment.parquet"
        if out_file.exists() and not overwrite:
            output_files[symbol] = out_file
            continue

        frame = _fetch_timeseries(symbol, start, end, api_key, interval=interval)
        if frame.empty:
            continue
        utils.write_time_series(frame, out_file)
        output_files[symbol] = out_file

    return output_files

