# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from . import utils

BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
BINANCE_OI_URL = "https://fapi.binance.com/futures/data/openInterestHist"
BINANCE_LIMIT = 1000


def _fetch_binance(
    url: str,
    symbol: str,
    start: datetime,
    end: datetime,
    limit: int = BINANCE_LIMIT,
    extra_params: dict[str, str] | None = None,
) -> pd.DataFrame:
    params: dict[str, str | int] = {
        "symbol": symbol,
        "limit": limit,
        **(extra_params or {}),
    }
    limiter = utils.RateLimiter(calls=110, period=60)  # Binance default IP limit

    rows: list[pd.DataFrame] = []
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    while start_ms < end_ms:
        limiter.wait()
        params["startTime"] = start_ms
        params["endTime"] = min(end_ms, start_ms + limit * 60 * 60 * 1000)
        payload = utils.json_request(url, params=params)
        frame = pd.DataFrame(payload)
        if frame.empty:
            break

        if "fundingTime" in frame.columns:
            frame["timestamp"] = pd.to_datetime(frame["fundingTime"], unit="ms", utc=True)
        elif "timestamp" in frame.columns:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
        else:
            frame["timestamp"] = pd.to_datetime(frame.iloc[:, 0], unit="ms", utc=True)
        frame = frame.set_index("timestamp").sort_index()
        rows.append(frame)

        last_ts = int(frame.index[-1].timestamp() * 1000)
        start_ms = last_ts + 1

    return utils.merge_frames(rows)


def run_pipeline(
    symbols: Iterable[str],
    out_dir: Path,
    quote: str = "USDT",
    overwrite: bool = False,
    lookback: timedelta = timedelta(days=365),
) -> dict[str, Path]:
    """
    Download funding rate and open-interest history from Binance futures.

    Parameters
    ----------
    symbols : iterable of str
        Base assets (e.g., "BTC", "ETH").
    out_dir : Path
        Target directory for `<symbol>_funding.parquet`.
    quote : str
        Quote currency (default: USDT).
    overwrite : bool
        Re-download even if cache exists.
    lookback : timedelta
        Time span to pull when overwriting/initializing.
    """

    utils.ensure_directory(out_dir)
    output_files: dict[str, Path] = {}
    end = datetime.now(tz=timezone.utc)
    start = end - lookback

    for symbol in symbols:
        market = f"{symbol.upper()}{quote.upper()}"
        out_file = out_dir / f"{symbol.lower()}_funding.parquet"
        if out_file.exists() and not overwrite:
            output_files[symbol] = out_file
            continue

        funding = _fetch_binance(BINANCE_FUNDING_URL, market, start, end)
        if not funding.empty:
            funding = funding.rename(
                columns={"fundingRate": "funding_rate", "symbol": "market"}
            )[["funding_rate", "market"]]
            funding["funding_rate"] = funding["funding_rate"].astype(float) * 100

        oi = _fetch_binance(
            BINANCE_OI_URL,
            market,
            start,
            end,
            extra_params={"period": "5m"},
        )
        if not oi.empty:
            oi = oi.rename(columns={"sumOpenInterest": "open_interest_usd"})[
                ["open_interest_usd"]
            ]
            oi["open_interest_usd"] = oi["open_interest_usd"].astype(float)

        combined = utils.merge_frames([funding, oi])
        if combined.empty:
            continue

        utils.write_time_series(combined, out_file)
        output_files[symbol] = out_file

    return output_files





