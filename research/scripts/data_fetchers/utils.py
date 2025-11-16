# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import pandas as pd
import requests

DEFAULT_HEADERS: Mapping[str, str] = {"User-Agent": "WealthLabs-Research/1.0"}


class RateLimiter:
    """Simple sleep-based rate limiter for politely hitting public APIs."""

    def __init__(self, calls: int, period: float) -> None:
        self.calls = calls
        self.period = period
        self._timestamps: list[float] = []

    def wait(self) -> None:
        now = time.time()
        self._timestamps = [ts for ts in self._timestamps if now - ts < self.period]
        if len(self._timestamps) >= self.calls:
            sleep_for = self.period - (now - self._timestamps[0]) + 0.01
            if sleep_for > 0:
                time.sleep(sleep_for)
        self._timestamps.append(time.time())


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def json_request(
    url: str,
    params: MutableMapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float = 30,
) -> Any:
    response = requests.get(
        url,
        params=params,
        headers=DEFAULT_HEADERS | (headers or {}),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def merge_frames(frames: Sequence[pd.DataFrame]) -> pd.DataFrame:
    valid = [df for df in frames if df is not None and not df.empty]
    if not valid:
        return pd.DataFrame()
    combined = pd.concat(valid, axis=0).sort_index()
    combined = combined[~combined.index.duplicated(keep="last")]
    return combined


def write_time_series(df: pd.DataFrame, out_file: Path) -> None:
    ensure_directory(out_file.parent)
    if out_file.suffix == ".parquet":
        df.to_parquet(out_file)
    elif out_file.suffix == ".csv":
        df.to_csv(out_file)
    else:
        out_file.write_text(df.to_json(orient="records"), encoding="utf-8")


def append_time_series(df: pd.DataFrame, out_file: Path) -> pd.DataFrame:
    if out_file.exists():
        existing = (
            pd.read_parquet(out_file)
            if out_file.suffix == ".parquet"
            else pd.read_csv(out_file, parse_dates=[0], index_col=0)
        )
        combined = merge_frames([existing, df])
    else:
        combined = df.sort_index()
    write_time_series(combined, out_file)
    return combined


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required for this pipeline.")
    return value


def chunked(iterable: Iterable[Any], size: int) -> Iterable[list[Any]]:
    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk





